from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_required
from .forms import CategoryForm, MenuItemForm
from .models import Category, MenuItem

@role_required('owner')
def manage_menu(request):
    return render(request,'menu/list.html',{'categories':Category.objects.prefetch_related('items')})

@role_required('owner')
def item_form(request, pk=None):
    item = get_object_or_404(MenuItem,pk=pk) if pk else None
    form = MenuItemForm(request.POST or None, instance=item)
    if request.method == 'POST' and form.is_valid(): form.save(); messages.success(request,'Item saved.'); return redirect('menu:manage')
    return render(request,'menu/form.html',{'form':form,'title':'Edit item' if item else 'New item'})

@role_required('owner')
def category_form(request, pk=None):
    category = get_object_or_404(Category,pk=pk) if pk else None
    form = CategoryForm(request.POST or None,instance=category)
    if request.method == 'POST' and form.is_valid(): form.save(); messages.success(request,'Category saved.'); return redirect('menu:manage')
    return render(request,'menu/form.html',{'form':form,'title':'Edit category' if category else 'New category'})

@role_required('owner')
def delete_object(request, kind, pk):
    model = MenuItem if kind == 'item' else Category
    obj = get_object_or_404(model,pk=pk)
    if request.method == 'POST': obj.delete(); messages.success(request,f'{kind.title()} deleted.'); return redirect('menu:manage')
    return render(request,'menu/delete.html',{'object':obj,'kind':kind})

@role_required('owner')
def toggle_item(request,pk):
    if request.method == 'POST':
        item=get_object_or_404(MenuItem,pk=pk); item.is_available=not item.is_available; item.save(update_fields=['is_available']); messages.success(request,'Availability updated.')
    return redirect('menu:manage')

from django.http import JsonResponse
def menu_json(request):
    data=[{'id':i.id,'name':i.name,'description':i.description,'price':str(i.price),'image_url':i.image_url,'available':i.is_available,'prep_minutes':i.prep_minutes,'category':i.category.name,'category_id':i.category_id} for i in MenuItem.objects.select_related('category').order_by('category__sort_order','name')]
    return JsonResponse({'items':data})
