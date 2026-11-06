from django.conf import settings
from django.db import models

class StaffProfile(models.Model):
    ROLES = [('kitchen','Kitchen'),('waiter','Waiter'),('owner','Owner')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)
    def __str__(self): return f'{self.user.username} ({self.role})'
