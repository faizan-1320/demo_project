from django.urls import path
from .views import *

urlpatterns = [
    path('cart/', cart_detail, name='cart-detail'),
    path('cart/add/<int:pk>/', add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:pk>/', remove_from_cart, name='remove-from-cart'),
    path('cart/update-cart-quantity/<int:pk>',update_cart_quantity,name='update-cart-quantity'),
    path('cart/checkout/',checkout,name='checkout'),
    path('payment/paypal/execute/', paypal_execute_payment, name='paypal_execute'),
    path('payment/paypal/cancel/', paypal_cancel_payment, name='paypal_cancel'),
    path('order-confirmation/<int:pk>', order_confirmation, name='order-confirmation'),
    path('user/orders/', order_list, name='order-user'),
    path('user/order/<int:pk>/', order_detail, name='user-order'),
]