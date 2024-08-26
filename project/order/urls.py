from django.urls import path
from .views import *

urlpatterns = [
    path('cart/', cart_detail, name='cart-detail'),
    path('cart/add/<int:pk>/', add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:pk>/', remove_from_cart, name='remove-from-cart'),
    path('cart/update-cart-quantity/<int:pk>',update_cart_quantity,name='update-cart-quantity')
]