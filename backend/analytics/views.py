from django.shortcuts import render
from accounts.decorators import role_required
from core.json import json_ok
from . import metrics
from .insights import generate_insights
@role_required('owner')
def dashboard(request):return render(request,'analytics/dashboard.html')
def _days(request):
    try:return max(7,min(60,int(request.GET.get('days',30))))
    except ValueError:return 30
def endpoint(name):
    def view(request):
        data=(generate_insights if name=='insights' else getattr(metrics,name))(_days(request))
        return json_ok({'results':data} if isinstance(data,list) else data)
    return role_required('owner',api=True)(view)
overview=endpoint('overview')
sales=endpoint('sales_by_day')
top=endpoint('top_items')
matrix=endpoint('menu_matrix')
heat=endpoint('heatmap')
prep=endpoint('prep_times')
insights=endpoint('insights')
