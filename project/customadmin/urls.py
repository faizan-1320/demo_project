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
    path('categories/add-sub-category/', add_sub_category, name='add-sub-category'),
    # Product URL
    path('products/', product, name='products'),
    path('products/add/', add_products, name='add-product'),
    path('products/<int:pk>/edit/', edit_product, name='edit-product'),
    path('products/<int:pk>/delete/', delete_product, name='delete-product'),
    path('products/add-attribute/', add_product_attribute, name='add-product-attribute'),
    path('products/add-attribute-value/', add_product_attribute_value, name='add-product-attribute-value'),
    # Banner URL
    path('banners/',banner,name='banners'),
    path('banners/add/',add_banner,name='add-banner'),
    path('banners/<int:pk>/delete/',delete_banner,name='delete-banner'),
    path('banners/<int:pk>/edit/',edit_banner,name='edit-banner'),
    # Contact_US URL
    path('contact-us/',contact_us,name='contact-us'),
    path('contact-us/<int:pk>/details',contact_us_detail,name='contact-us-details'),
    # FAQ URL
    path('flatpages/', flatpage_list, name='flatpages'),
    path('flatpages/add/',add_flatpage,name='add-flatpage'),
    path('flatpages/<int:pk>/edit',edit_flatpage,name='edit-flatpage'),
    path('flatpages/<int:pk>/delete',delete_flatpage,name='delete-flatpage'),
]