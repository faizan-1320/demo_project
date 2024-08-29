from django.urls import path
from .views import *
urlpatterns = [
    path('product/detail/<int:pk>/',product_detail,name='product-detail'),
    path('product/review/<int:product_id>/', product_review_and_rating, name='product-review-and-rating'),
]