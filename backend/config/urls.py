from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
def home(request): return render(request,'home.html')
def not_found(request, exception): return render(request,'404.html',status=404)
def server_error(request): return render(request,'500.html',status=500)
handler404 = 'config.urls.not_found'
handler500 = 'config.urls.server_error'
urlpatterns = [path('admin/',admin.site.urls),path('',home,name='home'),path('staff/',include('accounts.urls')),path('',include('menu.urls')),path('',include('tables.urls')),path('',include('orders.urls')),path('',include('analytics.urls'))]
