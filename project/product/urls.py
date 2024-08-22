from django.urls import path
from .views import *
urlpatterns = [
    path('product/detail/<int:pk>/',product_detail,name='product-detail'),
]