from django import forms
from .models import DiningTable
class DiningTableForm(forms.ModelForm):
    class Meta: model=DiningTable; fields=['number','is_active']
