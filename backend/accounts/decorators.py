from functools import wraps
from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

def role_required(*roles, api=False):
    def decorate(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error':'Authentication required'}, status=403) if api else redirect_to_login(request.get_full_path(), reverse('accounts:login'))
            profile = getattr(request.user, 'staffprofile', None)
            if not (request.user.is_superuser or profile and profile.role in roles):
                return JsonResponse({'error':'Permission denied'}, status=403) if api else HttpResponseForbidden('You do not have access to this page.')
            return view(request, *args, **kwargs)
        return wrapped
    return decorate
