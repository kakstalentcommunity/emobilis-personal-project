from django.db import models
from django.utils import timezone
from tables.models import TableSession
from menu.models import MenuItem
class Order(models.Model):
    STATUSES = [('received','Received'),('preparing','Preparing'),('ready','Ready'),('served','Served'),('cancelled','Cancelled')]
    session = models.ForeignKey(TableSession,on_delete=models.PROTECT,related_name='orders')
    status = models.CharField(max_length=20,choices=STATUSES,default='received')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    preparing_at = models.DateTimeField(null=True,blank=True)
    ready_at = models.DateTimeField(null=True,blank=True)
    served_at = models.DateTimeField(null=True,blank=True)
class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    menu_item = models.ForeignKey(MenuItem,on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=9,decimal_places=2)
    item_note = models.CharField(max_length=240,blank=True)
class Payment(models.Model):
    METHODS = [('cash','Cash'),('mpesa','M-Pesa')]
    session = models.ForeignKey(TableSession,on_delete=models.PROTECT,related_name='payments')
    method = models.CharField(max_length=10,choices=METHODS)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
