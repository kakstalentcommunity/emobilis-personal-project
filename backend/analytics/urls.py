from django.urls import path
from . import views
app_name='analytics'
urlpatterns=[path('owner/dashboard/',views.dashboard,name='dashboard'),path('api/owner/analytics/overview/',views.overview,name='overview'),path('api/owner/analytics/sales-by-day/',views.sales,name='sales'),path('api/owner/analytics/top-items/',views.top,name='top'),path('api/owner/analytics/menu-matrix/',views.matrix,name='matrix'),path('api/owner/analytics/heatmap/',views.heat,name='heatmap'),path('api/owner/analytics/prep-times/',views.prep,name='prep'),path('api/owner/analytics/insights/',views.insights,name='insights')]
