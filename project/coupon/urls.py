from django.urls import path
from .views import *

urlpatterns = [
    path('coupons/',coupon,name='coupon'),
    path('coupons/create/', add_coupon, name='add-coupon'),
    path('coupons/<int:pk>/edit/', edit_coupon, name='edit-coupon'),
    path('coupons/<int:pk>/delete/', delete_coupon, name='delete-coupon'),
]