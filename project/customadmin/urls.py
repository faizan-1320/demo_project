from django.urls import path
from .views import *

urlpatterns = [
    path('', adminlogin, name='adminlogin'),
    path('logout-admin/', logoutadmin, name='logout-admin'),
    path('dashboard/', dashboard, name='dashboard'),
    # User URL
    path('users/', users, name='users'),
    path('users/add/', add_users, name='add-user'),
    path('users/<int:pk>/delete/', delete_user, name='user-delete'),
    path('users/<int:pk>/edit/', edit_user, name='user-edit'),
    # Category URL
    path('categories/', category, name='categories'),
    path('categories/add/', add_category, name='add-category'),
    path('categories/<int:pk>/edit/', edit_category, name='edit-category'),
    path('categories/<int:pk>/delete/', delete_category, name='delete-category'),
    # Product URL
    path('products/', product, name='products'),
    path('products/add/', add_products, name='add-product'),
    path('products/<int:pk>/edit/', edit_product, name='edit-product'),
    path('products/<int:pk>/delete/', delete_product, name='delete-product'),
    path('products/add-attribute/', add_product_attribute, name='add-product-attribute'),
    # Banner URL
    path('banners/',banner,name='banners'),
    path('banners/add/',add_banner,name='add-banner'),
    path('banners/<int:pk>/delete/',delete_banner,name='delete-banner'),
    path('banners/<int:pk>/edit/',edit_banner,name='edit-banner'),
    # Contact_US URL
    path('contact-us/',contact_us,name='contact-us'),
    path('contact-us/<int:pk>/details',contact_us_detail,name='contact-us-details'),
    # CMS URL
    path('cms/', flatpage_list, name='cms'),
    path('cms/add/',add_flatpage,name='add-flatpage'),
    path('cms/<int:pk>/edit',edit_flatpage,name='edit-flatpage'),
    path('cms/<int:pk>/delete',delete_flatpage,name='delete-flatpage'),
    # Email URL
    path('emails/',email_template,name='emails'),
    path('emails/add',add_template,name='email-add'),
    path('emails/<int:pk>/edit/', edit_email_template, name='edit-email'),
    path('emails/<int:pk>/delete/', delete_email_template, name='delete-email'),
    # Order URL
    path('orders/', order, name='orders'),
    path('orders/<int:pk>/detail', order_detail, name='order-detail'),
]