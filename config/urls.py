"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def custom_page_not_found_view(request, exception):
    """Custom view to handle 404 errors."""
    return render(request, '404_error.html', {'exception': exception}, status=404)

def custom_permission_denied_view(request, exception):
    """Custom view to handle 403 errors."""
    return render(request, '403_error.html', {'exception': exception}, status=403)

handler404 = custom_page_not_found_view
handler403 = custom_permission_denied_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('project.users.urls')),
    path('',include('project.product.urls')),
    path('',include('project.order.urls')),
    path('',include('allauth.urls')),
    path('admin-custom/',include('project.customadmin.urls')),
    path('admin-custom/',include('project.coupon.urls')),
    path("pages/", include("django.contrib.flatpages.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
