from django.urls import path
from . import views
app_name='orders'
urlpatterns=[path('t/<str:qr_code>/',views.diner,name='diner'),path('staff/kitchen/',views.kitchen_page,name='kitchen'),path('staff/waiter/',views.waiter_page,name='waiter'),path('api/table/<str:qr_code>/orders/',views.table_orders,name='table_orders'),path('api/table/<str:qr_code>/orders/new/',views.create_order,name='create_order'),path('api/table/<str:qr_code>/bill/',views.request_bill,name='request_bill'),path('api/kitchen/orders/',views.kitchen_orders,name='kitchen_orders'),path('api/orders/<int:pk>/status/',views.update_status,name='update_status'),path('api/waiter/tables/',views.waiter_tables,name='waiter_tables'),path('api/sessions/<int:pk>/close/',views.close_bill,name='close_bill')]
