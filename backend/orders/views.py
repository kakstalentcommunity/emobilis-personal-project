from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse
from django.utils import timezone
from accounts.decorators import role_required
from core.json import json_body, json_error, json_ok
from tables.models import DiningTable, TableSession
from .models import Order
from .services import session_total, estimated_wait, change_status, close_session, place_order

def _item_dict(item): return {'id':item.menu_item_id,'name':item.menu_item.name,'quantity':item.quantity,'price':str(item.unit_price),'note':item.item_note,'total':str(item.unit_price*item.quantity)}
def _order_dict(order): return {'id':order.id,'status':order.status,'note':order.note,'created_at':order.created_at.isoformat(),'minutes_waiting':max(0,int((timezone.now()-order.created_at).total_seconds()/60)),'items':[_item_dict(row) for row in order.items.select_related('menu_item')]}

@ensure_csrf_cookie
def diner(request,qr_code):
    table=get_object_or_404(DiningTable,qr_code=qr_code,is_active=True)
    session,_=TableSession.objects.get_or_create(table=table,status='open',defaults={'guests':1})
    items=[{'id':item.id,'name':item.name,'description':item.description,'price':str(item.price),'image_url':item.image_url,'available':item.is_available,'prep_minutes':item.prep_minutes,'category':item.category.name,'category_id':item.category_id} for item in __import__('menu.models',fromlist=['MenuItem']).MenuItem.objects.select_related('category').order_by('category__sort_order','name')]
    return render(request,'orders/diner.html',{'table':table,'session':session,'menu_json':items})

@require_GET
def table_orders(request,qr_code):
    table=get_object_or_404(DiningTable,qr_code=qr_code,is_active=True)
    session=TableSession.objects.filter(table=table,status__in=['open','awaiting_payment']).order_by('-opened_at').first()
    if not session:return json_ok({'orders':[],'total':'0.00','wait_minutes':0,'session_status':'closed'})
    orders=list(session.orders.exclude(status='cancelled').order_by('created_at'))
    return json_ok({'orders':[_order_dict(order) for order in orders],'total':str(session_total(session)),'wait_minutes':estimated_wait(session),'session_status':session.status})

@require_POST
def create_order(request,qr_code):
    table=get_object_or_404(DiningTable,qr_code=qr_code,is_active=True);session=get_object_or_404(TableSession,table=table,status='open')
    try: data=json_body(request); order=place_order(session,data.get('items'),data.get('note',''))
    except ValueError as error:return json_error(error)
    return json_ok({'order':_order_dict(order),'wait_minutes':estimated_wait(session)},201)

@require_POST
def request_bill(request,qr_code):
    table=get_object_or_404(DiningTable,qr_code=qr_code,is_active=True);session=get_object_or_404(TableSession,table=table,status__in=['open','awaiting_payment'])
    session.status='awaiting_payment';session.save(update_fields=['status'])
    return json_ok({'session_status':session.status,'total':str(session_total(session))})

@role_required('kitchen','owner')
def kitchen_page(request):return render(request,'orders/kitchen.html')
@role_required('waiter','owner')
def waiter_page(request):return render(request,'orders/waiter.html')

@require_GET
@role_required('kitchen','owner',api=True)
def kitchen_orders(request):
    orders=Order.objects.filter(status__in=['received','preparing']).select_related('session__table').prefetch_related('items__menu_item').order_by('created_at')
    return json_ok({'orders':[dict(_order_dict(o),table_number=o.session.table.number) for o in orders]})

@require_POST
@role_required('kitchen','waiter','owner',api=True)
def update_status(request,pk):
    order=get_object_or_404(Order.objects.select_related('session__table'),pk=pk)
    try:
        target=json_body(request).get('status')
        role=getattr(getattr(request.user,'staffprofile',None),'role','owner' if request.user.is_superuser else '')
        allowed=({'received','preparing','ready'} if role=='kitchen' else {'served','cancelled'} if role=='waiter' else {'preparing','ready','served','cancelled'})
        if target not in allowed:raise ValueError('Your role cannot set that order status.')
        change_status(order,target)
    except ValueError as error:return json_error(error)
    return json_ok({'order':_order_dict(order)})

@require_GET
@role_required('waiter','owner',api=True)
def waiter_tables(request):
    tables=[]
    for table in DiningTable.objects.filter(is_active=True).order_by('number'):
        session=table.sessions.filter(status__in=['open','awaiting_payment']).order_by('-opened_at').first()
        if session:tables.append({'id':table.id,'number':table.number,'session_id':session.id,'session_status':session.status,'total':str(session_total(session)),'ready':session.orders.filter(status='ready').exists(),'orders':[_order_dict(o) for o in session.orders.exclude(status='cancelled').order_by('-created_at')]})
    return json_ok({'tables':tables})

@require_POST
@role_required('waiter','owner',api=True)
def close_bill(request,pk):
    session=get_object_or_404(TableSession,pk=pk)
    try: payment=close_session(session,json_body(request).get('method'))
    except ValueError as error:return json_error(error)
    return json_ok({'payment_id':payment.id,'amount':str(payment.amount),'session_status':'closed'})
