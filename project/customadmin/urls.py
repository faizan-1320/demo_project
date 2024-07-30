from django.conf import settings
from django.conf.urls.static import static
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
    path('edit-category/',edit_category,name='edit-category'),
    path('delete-category/<int:pk>',delete_category,name='delete-category'),
    path('add-sub-category/',add_sub_category,name='add-sub-category'),
    # Product
    path('products/',product,name='products'),
    path('add-product/',add_products,name='add-product'),
    path('add-product-attribute/',add_product_attribute,name='add-product-attribute'),
    path('add-product-attribute-value/',add_product_attribute_value,name='add-product-attribute-value')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    print('static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT): ', static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))