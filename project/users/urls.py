from django.urls import path
from .views import *
urlpatterns = [
    path('',home,name='home'),
    path('auth-view/',auth_view,name='auth-view'),
    path('logout/',logoutUser,name='logout'),
    path('forgot-password/',forgot_password,name='forgot-password'),
    path('contact-us/',contact_us,name='contact'),
    path('user/detail',user_detail,name='user'),
    path('user/detail/edit',user_detail_edit,name='user-edit'),
    path('user/add/address',add_address,name='add-address'),
    path('user/edit/address/<int:pk>',edit_address,name='edit-address'),
    path('user/delete/address/<int:pk>',delete_address,name='delete-address'),
]