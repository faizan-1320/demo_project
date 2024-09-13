"""
URL configuration for the Coupon application.

This module defines the URL patterns for managing coupons, including listing,
creating, editing, and deleting coupons.
"""

from django.urls import path
from .views import coupon_list, add_coupon, edit_coupon, delete_coupon

urlpatterns = [
    path('coupons/', coupon_list, name='coupons'),
    path('coupons/create/', add_coupon, name='add-coupon'),
    path('coupons/<int:pk>/edit/', edit_coupon, name='edit-coupon'),
    path('coupons/<int:pk>/delete/', delete_coupon, name='delete-coupon'),
]
