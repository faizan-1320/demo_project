from django.urls import path
from .views import *

urlpatterns = [
    path('',adminlogin,name='adminlogin'),
    path('logout-admin/',logoutadmin,name='logout-admin'),
    path('dashboard/',dashboard,name='dashboard'),
    # User URL
    path('users/',users,name='users'),
    path('add-user/',add_users,name='add-user'),
    path('user-delete/<int:pk>/', delete_user, name='user-delete'),
    path('user-edit/<int:pk>/', edit_user, name='user-edit'),
    # Category URL
    path('categories/',category,name='categories'),
    path('add-category/',add_category,name='add-category'),
    path('add-sub-category/',add_sub_category,name='add-sub-category'),
    # Product
    path('add-product-attribute/',add_product_attribute,name='add-product-attribute')
]