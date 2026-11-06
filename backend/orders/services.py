from datetime import timedelta
from django.db import transaction
from django.db.models import Avg
from django.utils import timezone
from tables.models import TableSession
from .models import Order, OrderItem, Payment
from menu.models import MenuItem

TRANSITIONS={'received':{'preparing','cancelled'},'preparing':{'ready','cancelled'},'ready':{'served','cancelled'},'served':set(),'cancelled':set()}
@transaction.atomic
def change_status(order,status):
    if status not in TRANSITIONS.get(order.status,set()): raise ValueError(f'Cannot move an order from {order.status} to {status}.')
    now=timezone.now(); order.status=status
    if status=='preparing': order.preparing_at=now
    if status=='ready': order.ready_at=now
    if status=='served': order.served_at=now
    order.save(update_fields=['status','preparing_at','ready_at','served_at'])
    return order

def session_total(session):
    from django.db.models import F,Sum,ExpressionWrapper,DecimalField
    return session.orders.exclude(status='cancelled').aggregate(total=Sum(ExpressionWrapper(F('items__quantity')*F('items__unit_price'),output_field=DecimalField(max_digits=12,decimal_places=2))))['total'] or 0

def estimated_wait(session, new_items=None):
    # Keep the estimate conservative when no completed-order history is available.
    history=Order.objects.filter(status='ready',ready_at__isnull=False).values_list('created_at','ready_at')
    durations=[(ready-created).total_seconds()/60 for created,ready in history[:500]]
    per_order=sum(durations)/len(durations) if durations else 12
    ahead=session.orders.filter(status__in=['received','preparing']).count()
    item_minutes=sum(item.prep_minutes for item in (new_items or []))
    return max(1,round(per_order*(ahead+1))) if durations else max(1,item_minutes or round(per_order*(ahead+1)))

@transaction.atomic
def close_session(session,method):
    if method not in {'cash','mpesa'}: raise ValueError('Choose cash or M-Pesa.')
    if session.status=='closed': raise ValueError('This bill is already closed.')
    amount=session_total(session)
    payment=Payment.objects.create(session=session,method=method,amount=amount)
    session.status='closed';session.closed_at=timezone.now();session.save(update_fields=['status','closed_at'])
    return payment

@transaction.atomic
def place_order(session,items,note=''):
    if session.status!='open': raise ValueError('This table is not accepting orders right now.')
    if not isinstance(items,list) or not items: raise ValueError('Add at least one item.')
    ids=[]
    for row in items:
        try: mid=int(row['menu_item_id']); quantity=int(row['quantity'])
        except (KeyError,ValueError,TypeError): raise ValueError('Each item needs a menu item and quantity.')
        if quantity<1 or quantity>20: raise ValueError('Quantities must be between 1 and 20.')
        ids.append(mid)
    products={item.id:item for item in MenuItem.objects.filter(id__in=ids,is_available=True)}
    if len(products)!=len(set(ids)): raise ValueError('One or more items are unavailable.')
    order=Order.objects.create(session=session,note=str(note)[:500])
    for row in items:
        product=products[int(row['menu_item_id'])]
        OrderItem.objects.create(order=order,menu_item=product,quantity=int(row['quantity']),unit_price=product.price,item_note=str(row.get('item_note',''))[:240])
    return order
