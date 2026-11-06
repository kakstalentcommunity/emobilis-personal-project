from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect,render
from django.http import HttpResponse
from accounts.decorators import role_required
from .models import DiningTable
from .forms import DiningTableForm
from .qr import qr_svg

@role_required('owner')
def manage(request): return render(request,'tables/list.html',{'tables':DiningTable.objects.all()})
@role_required('owner')
def create(request):
    form=DiningTableForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Table saved.'); return redirect('tables:manage')
    return render(request,'tables/form.html',{'form':form})
@role_required('owner')
def action(request,pk,action):
    if request.method=='POST':
        table=get_object_or_404(DiningTable,pk=pk)
        if action=='toggle': table.is_active=not table.is_active
        else: table.qr_code=''
        table.save(); messages.success(request,'Table updated.')
    return redirect('tables:manage')
@role_required('owner')
def qr(request,pk): return HttpResponse(qr_svg(get_object_or_404(DiningTable,pk=pk)),content_type='image/svg+xml')
@role_required('owner')
def print_cards(request): return render(request,'tables/print.html',{'tables':DiningTable.objects.filter(is_active=True)})
