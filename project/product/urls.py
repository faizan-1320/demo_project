"""
URL configurations for the custom admin panel. 
Includes routes for managing product_detail,product_review_and_rating,product.
"""
from django.urls import path
from .views import product_detail,product_review_and_rating
from .admin_view import (product, add_products,
    edit_product, delete_product, product_attribute, add_product_attribute,
    edit_product_attribute, delete_product_attribute,
    category, add_category, edit_category, delete_category)

urlpatterns = [
    path('product/detail/<int:pk>/',product_detail,name='product-detail'),
    path('product/review/<int:product_id>/',
    product_review_and_rating, name='product-review-and-rating'),
    # Admin Product URL
    path('products/', product, name='products'),
    path('products/add/', add_products, name='add-product'),
    path('products/<int:pk>/edit/', edit_product, name='edit-product'),
    path('products/<int:pk>/delete/', delete_product, name='delete-product'),
    path('products/attribute/', product_attribute, name='product-attribute'),
    path('products/add-attribute/', add_product_attribute, name='add-product-attribute'),
    path('products/<int:pk>/edit-attribute/', edit_product_attribute, name='edit-attribute'),
    path('products/<int:pk>/delete-attribute/', delete_product_attribute, name='delete-attribute'),
    # Admin Category URL
    path('categories/', category, name='categories'),
    path('categories/add/', add_category, name='add-category'),
    path('categories/<int:pk>/edit/', edit_category, name='edit-category'),
    path('categories/<int:pk>/delete/', delete_category, name='delete-category'),
]
