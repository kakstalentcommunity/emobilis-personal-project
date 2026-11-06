from django.urls import path
from . import views
app_name='menu'
urlpatterns=[path('owner/menu/',views.manage_menu,name='manage'),path('owner/menu/items/new/',views.item_form,name='item_new'),path('owner/menu/items/<int:pk>/edit/',views.item_form,name='item_edit'),path('owner/menu/items/<int:pk>/delete/',views.delete_object,{'kind':'item'},name='item_delete'),path('owner/menu/categories/new/',views.category_form,name='category_new'),path('owner/menu/categories/<int:pk>/edit/',views.category_form,name='category_edit'),path('owner/menu/categories/<int:pk>/delete/',views.delete_object,{'kind':'category'},name='category_delete'),path('owner/menu/items/<int:pk>/toggle/',views.toggle_item,name='item_toggle'),path('api/menu/',views.menu_json,name='api_menu')]
