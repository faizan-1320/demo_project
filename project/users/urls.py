"""
URL configurations for the custom admin panel. 
Includes routes for managing product_detail,product_review_and_rating,product.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (home,auth_view,logout_user,contact_us,user_detail_edit,
        user_detail,add_address,edit_address,delete_address,wish_list,
        remove_from_wishlist,add_to_wishlist)
urlpatterns = [
    # Home Page
    path('',home,name='home'),
    # Auth URL
    path('auth-view/',auth_view,name='auth-view'),
    path('logout/',logout_user,name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html'), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'), name='password_change_done'),
    # Contact US URL
    path('contact-us/',contact_us,name='contact'),
    # User Detail URL
    path('user/detail',user_detail,name='user'),
    path('user/detail/edit',user_detail_edit,name='user-edit'),
    # Address URL
    path('user/add/address',add_address,name='add-address'),
    path('user/edit/address/<int:pk>',edit_address,name='edit-address'),
    path('user/delete/address/<int:pk>',delete_address,name='delete-address'),
    # WishList URL
    path('wishlist/',wish_list,name='wishlist'),
    path('wishlist/add/<int:product_id>/',add_to_wishlist,name='add-to-wishlist'),
    path('wishlist/remove/<int:product_id>/',remove_from_wishlist,name='remove-from-wishlist'),

]
