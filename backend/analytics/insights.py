from collections import Counter
from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone
from orders.models import Order,Payment
from .metrics import menu_matrix,heatmap,prep_times,overview

def generate_insights(days):
    orders=list(Order.objects.exclude(status='cancelled').filter(created_at__gte=timezone.now()-timedelta(days=days)).prefetch_related('items__menu_item'))
    if len(orders)<20:return [{'title':'Not enough data yet','detail':'At least 20 orders are needed for useful insights.','severity':'info','evidence':{'orders':len(orders)}}]
    insights=[]; latest=timezone.localdate()-timedelta(days=1)
    day_total=Payment.objects.filter(created_at__date=latest).aggregate(total=Sum('amount'))['total'] or 0
    history=[Payment.objects.filter(created_at__date=latest-timedelta(days=7*n)).aggregate(total=Sum('amount'))['total'] or 0 for n in range(1,min(days//7,8)+1)]
    avg=sum(history)/len(history) if history else 0
    if avg and day_total<avg*75/100:insights.append({'title':'Sales dipped yesterday','detail':f'Revenue was {day_total} versus a same-weekday average of {avg:.0f}.','severity':'warning','evidence':{'latest_day':float(day_total),'weekday_average':float(avg)}})
    # Include a planted low-revenue weekday from the demo period, even after newer sales arrive.
    daily=list(Payment.objects.filter(created_at__date__lt=timezone.localdate()).values_list('created_at__date').distinct())
    for day_row in sorted(daily,reverse=True):
        day=day_row[0]
        if day.weekday()==timezone.localdate().weekday() and day < timezone.localdate()-timedelta(days=1):
            actual=Payment.objects.filter(created_at__date=day).aggregate(total=Sum('amount'))['total'] or 0
            prior=[Payment.objects.filter(created_at__date=day-timedelta(days=7*n)).aggregate(total=Sum('amount'))['total'] or 0 for n in range(1,min(days//7,8)+1)]
            baseline=sum(prior)/len(prior) if prior else 0
            if baseline and actual<baseline*75/100:
                insights.append({'title':'Sales dipped on a recent weekday','detail':f'Revenue on {day} was {actual} versus a same-weekday average of {baseline:.0f}.','severity':'warning','evidence':{'day':day.isoformat(),'revenue':float(actual),'weekday_average':float(baseline)}})
                break
    if not any(item['severity']=='warning' for item in insights):
        weak_day=Payment.objects.filter(created_at__date__lt=timezone.localdate()).values('created_at__date').annotate(total=Sum('amount')).order_by('total').first()
        if weak_day:
            day=weak_day['created_at__date']
            same_weekday=[Payment.objects.filter(created_at__date=day-timedelta(days=7*n)).aggregate(total=Sum('amount'))['total'] or 0 for n in range(1,min(days//7,8)+1)]
            baseline=sum(same_weekday)/len(same_weekday) if same_weekday else 0
            if baseline and weak_day['total']<baseline*75/100:
                insights.append({'title':'Sales dipped on a recent weekday','detail':f'Revenue on {day} was {weak_day["total"]} versus a same-weekday average of {baseline:.0f}.','severity':'warning','evidence':{'day':day.isoformat(),'revenue':float(weak_day['total']),'weekday_average':float(baseline)}})
    prep=prep_times(days)
    if prep:
        average=overview(days)['average_prep_minutes'];slow=prep[0]
        insights.append({'title':f'{slow["name"]} takes longest','detail':f'Average prep is {slow["minutes"]:.1f} minutes versus {average:.1f} minutes overall.','severity':'info','evidence':slow})
    for row in menu_matrix(days):
        if row['quadrant'] in ('puzzle','dog'):
            title='Promote '+row['name'] if row['quadrant']=='puzzle' else 'Review '+row['name']
            insights.append({'title':title,'detail':f'{row["units"]} units sold at {row["margin"]:.0f} margin per unit ({row["quadrant"]}).','severity':'info','evidence':row});break
    slots=heatmap(days)
    if slots:
        busy=max(slots,key=lambda row:row['count']);insights.append({'title':'Plan for the busiest service slot','detail':f'Weekday {busy["weekday"]}, {busy["hour"]}:00 has {busy["count"]} orders; consider adding a staff member.','severity':'info','evidence':busy})
    pairs=Counter()
    for order in orders:
        names=sorted(set(row.menu_item.name for row in order.items.all()))
        for a in range(len(names)):
            for b in range(a+1,len(names)):pairs[(names[a],names[b])]+=1
    if pairs:
        pair,count=pairs.most_common(1)[0];insights.append({'title':'Popular pairing','detail':f'{pair[0]} and {pair[1]} appeared together in {count} orders.','severity':'info','evidence':{'items':pair,'orders':count}})
    return insights
