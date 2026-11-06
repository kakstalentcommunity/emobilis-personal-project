from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

class StaffLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

@login_required
def role_redirect(request):
    if request.user.is_superuser: return redirect('analytics:dashboard')
    role = getattr(getattr(request.user, 'staffprofile', None), 'role', '')
    return redirect({'owner':'analytics:dashboard','kitchen':'orders:kitchen','waiter':'orders:waiter'}.get(role, 'accounts:login'))

class StaffLogoutView(LogoutView):
    next_page = 'home'
