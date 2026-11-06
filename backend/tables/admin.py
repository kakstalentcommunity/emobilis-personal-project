from django.contrib import admin
from .models import DiningTable, TableSession
@admin.register(DiningTable)
class DiningTableAdmin(admin.ModelAdmin): list_display = ('number','qr_code','is_active')
@admin.register(TableSession)
class TableSessionAdmin(admin.ModelAdmin): list_display = ('table','guests','status','opened_at')
