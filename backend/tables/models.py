from django.db import models
from django.utils.crypto import get_random_string
class DiningTable(models.Model):
    number = models.PositiveIntegerField(unique=True)
    qr_code = models.CharField(max_length=10, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    def save(self,*args,**kwargs):
        if not self.qr_code: self.qr_code = get_random_string(10)
        super().save(*args,**kwargs)
    def __str__(self): return f'Table {self.number}'
class TableSession(models.Model):
    STATUSES = [('open','Open'),('awaiting_payment','Awaiting payment'),('closed','Closed')]
    table = models.ForeignKey(DiningTable,on_delete=models.PROTECT,related_name='sessions')
    guests = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20,choices=STATUSES,default='open')
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True,blank=True)
