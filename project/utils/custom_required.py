"""Custom required"""

from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse

def check_login_admin(user):
    """Login Required For Admin Function"""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.groups.filter(name__in=['inventory manager','order manager']).exists():
        return True
    return False

def admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        # Check if the user is authenticated and has the required permissions
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('adminlogin'))  # Redirect to the login page if not authenticated
        if request.user.is_superuser or request.user.groups.filter(name__in=['inventory manager', 'order manager']).exists():
            return function(request, *args, **kwargs)  # Proceed if the user is a superuser or belongs to the specified groups
        return HttpResponseRedirect(reverse('permission_denied'))  # Redirect to a permission denied page if not authorized
    return wrap
