from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
urlpatterns = [
    # Home Page
    path('',home,name='home'),
    # Auth URL
    path('auth-view/',auth_view,name='auth-view'),
    path('logout/',logoutUser,name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # Contact US URL
    path('contact-us/',contact_us,name='contact'),
    # User Detail URL
    path('user/detail',user_detail,name='user'),
    path('user/detail/edit',user_detail_edit,name='user-edit'),
    # Address URL
    path('user/add/address',add_address,name='add-address'),
    path('user/edit/address/<int:pk>',edit_address,name='edit-address'),
    path('user/delete/address/<int:pk>',delete_address,name='delete-address'),
    
]