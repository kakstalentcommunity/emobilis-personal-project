from django.urls import path
from . import views
app_name='tables'
urlpatterns=[path('owner/tables/',views.manage,name='manage'),path('owner/tables/new/',views.create,name='create'),path('owner/tables/print/',views.print_cards,name='print'),path('owner/tables/<int:pk>/qr.svg',views.qr,name='qr'),path('owner/tables/<int:pk>/<str:action>/',views.action,name='action')]
