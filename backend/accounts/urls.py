from django.urls import path
from .views import StaffLoginView, StaffLogoutView, role_redirect
app_name = 'accounts'
urlpatterns = [path('login/', StaffLoginView.as_view(), name='login'),path('logout/',StaffLogoutView.as_view(),name='logout'),path('redirect/',role_redirect,name='redirect')]
