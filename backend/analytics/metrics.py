from datetime import timedelta
from django.db.models import Sum,Count,Avg,F,ExpressionWrapper,DecimalField,DurationField
from django.db.models.functions import TruncDate,ExtractWeekDay,ExtractHour
from django.utils import timezone
from orders.models import Order,OrderItem,Payment

def _bounds(days):
    end=timezone.now();start=end-timedelta(days=days)
    return start,end
def overview(days):
    start,end=_bounds(days); prev_start=start-timedelta(days=days)
    def stats(a,b):
        payments=Payment.objects.filter(created_at__gte=a,created_at__lt=b)
        revenue=payments.aggregate(value=Sum('amount'))['value'] or 0
        orders=Order.objects.filter(created_at__gte=a,created_at__lt=b).exclude(status='cancelled')
        count=orders.count();prep=orders.exclude(ready_at=None).annotate(minutes=ExpressionWrapper(F('ready_at')-F('created_at'),output_field=DurationField())).aggregate(avg=Avg('minutes'))['avg']
        guests=orders.values('session_id').distinct().count()
        return {'revenue':float(revenue),'orders':count,'average_order_value':float(revenue/count) if count else 0,'average_prep_minutes':prep.total_seconds()/60 if prep else 0,'revenue_per_guest':float(revenue/guests) if guests else 0}
    current=stats(start,end);previous=stats(prev_start,start)
    return {**current,'changes':{key:((current[key]-previous[key])/previous[key]*100 if previous[key] else 0) for key in current}}
def sales_by_day(days):
    start,end=_bounds(days)
    values=Payment.objects.filter(created_at__gte=start,created_at__lt=end).annotate(day=TruncDate('created_at')).values('day').annotate(revenue=Sum('amount')).order_by('day')
    result={row['day']:row['revenue'] for row in values}
    return [{'day':(start.date()+timedelta(days=index)).isoformat(),'revenue':float(result.get(start.date()+timedelta(days=index),0))} for index in range(days)]
def top_items(days):
    start,end=_bounds(days)
    q=OrderItem.objects.filter(order__created_at__gte=start,order__created_at__lt=end).exclude(order__status='cancelled').values('menu_item__id','menu_item__name').annotate(units=Sum('quantity'),revenue=Sum(F('quantity')*F('unit_price'),output_field=DecimalField(max_digits=12,decimal_places=2))).order_by('-units')
    return list(q)
def menu_matrix(days):
    sold=top_items(days); from menu.models import MenuItem
    rows=[]
    for item in MenuItem.objects.all():
        match=next((x for x in sold if x['menu_item__id']==item.id),None);units=match['units'] if match else 0
        rows.append({'id':item.id,'name':item.name,'units':units,'margin':float(item.price-item.cost_price),'revenue':float(match['revenue']) if match else 0})
    avg_units=sum(r['units'] for r in rows)/len(rows) if rows else 0;avg_margin=sum(r['margin'] for r in rows)/len(rows) if rows else 0
    for row in rows:row['quadrant']=('star' if row['units']>=avg_units and row['margin']>=avg_margin else 'plowhorse' if row['units']>=avg_units else 'puzzle' if row['margin']>=avg_margin else 'dog')
    return rows
def heatmap(days):
    start,end=_bounds(days)
    rows=Order.objects.filter(created_at__gte=start,created_at__lt=end).exclude(status='cancelled').annotate(weekday=ExtractWeekDay('created_at'),hour=ExtractHour('created_at')).values('weekday','hour').annotate(count=Count('id')).order_by('weekday','hour')
    return [{'weekday':row['weekday'],'hour':row['hour'],'count':row['count']} for row in rows]
def prep_times(days):
    start,end=_bounds(days)
    q=OrderItem.objects.filter(order__created_at__gte=start,order__created_at__lt=end,order__ready_at__isnull=False).annotate(minutes=ExpressionWrapper(F('order__ready_at')-F('order__created_at'),output_field=DurationField())).values('menu_item__name').annotate(average=Avg('minutes'),units=Sum('quantity')).order_by('-average')
    return [{'name':x['menu_item__name'],'minutes':x['average'].total_seconds()/60 if x['average'] else 0,'units':x['units']} for x in q]
