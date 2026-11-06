from django import forms
from .models import Category, MenuItem
class CategoryForm(forms.ModelForm):
    class Meta: model = Category; fields = ['name','sort_order']
class MenuItemForm(forms.ModelForm):
    class Meta: model = MenuItem; fields = ['category','name','description','price','cost_price','image_url','is_available','prep_minutes']
