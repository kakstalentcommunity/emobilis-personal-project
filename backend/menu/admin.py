from django.contrib import admin
from .models import Category, MenuItem
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): list_display = ('name','sort_order')
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin): list_display = ('name','category','price','is_available')
