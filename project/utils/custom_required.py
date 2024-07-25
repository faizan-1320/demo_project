from django.contrib.auth.models import Group

def check_login_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.groups.filter(name__in=['inventory manager','order manager']).exists():
        return True
    return False

def role_manage(user):
    user_role = None
    if user.groups.filter(name='inventory manager').exists():
        user_role = 'inventory manager'
    elif user.groups.filter(name='order manager').exists():
        user_role = 'order manager'
    elif user.is_superuser:
        user_role = 'Admin'
    return user_role

from functools import wraps
from django.http import HttpResponseForbidden

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_profile = getattr(request.user, 'profile', None)  # Adjust this based on your user profile setup
            if request.user.is_superuser or (user_profile and user_profile.role == required_role):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have permission to access this page.")
        return _wrapped_view
    return decorator
