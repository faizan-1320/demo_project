"""
URL configurations for the custom admin panel. 
Includes routes for managing cart,order,payment.
"""
from django.urls import path
from .views import (
    cart_detail,add_to_cart,remove_from_cart,
    update_cart_quantity,checkout,paypal_cancel_payment
    ,paypal_execute_payment,order_confirmation,track_order,
    order_detail_user,order_list,paypal_webhook,generate_invoice_pdf,invoice_view
)
from .admin_view import order, order_detail

urlpatterns = [
    path('cart/', cart_detail, name='cart-detail'),
    path('cart/add/<int:pk>/', add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:pk>/', remove_from_cart, name='remove-from-cart'),
    path('cart/update-cart-quantity/<int:pk>',update_cart_quantity,name='update-cart-quantity'),
    path('cart/checkout/',checkout,name='checkout'),
    path('payment/paypal/execute/', paypal_execute_payment, name='paypal_execute'),
    path('payment/paypal/cancel/', paypal_cancel_payment, name='paypal_cancel'),
    path('payment/paypal/webhook/', paypal_webhook, name='paypal_webhook'),
    path('order-confirmation/<int:pk>', order_confirmation, name='order-confirmation'),
    path('user/orders/', order_list, name='order-user'),
    path('user/order/<int:pk>/', order_detail_user, name='user-order'),
    path('user/order/track-order/', track_order, name='track-order'),
    path('download-invoice/<int:order_id>/', generate_invoice_pdf, name='generate-invoice-pdf'),
    path('download-invoice-html/<int:order_id>/', invoice_view, name='generate-html-invoice-pdf'),
    # Admin Order URL
    path('admin-custom/orders/', order, name='orders'),
    path('admin-custom/orders/<int:pk>/detail', order_detail, name='order-detail'),
]
