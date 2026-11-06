from django.contrib import admin
from .models import Order, OrderItem, Payment
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin): list_display = ('id','session','status','created_at')
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin): list_display = ('order','menu_item','quantity','unit_price')
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin): list_display = ('session','method','amount','created_at')
