from django.urls import path
from .views import *
urlpatterns = [
    path('',home,name='home'),
    path('login/',view_login,name='login'),
    path('logout/',logoutUser,name='logout'),
    path('registration/',registerPage,name='registration'),
    path('forgot-password/',forgot_password,name='forgot-password'),
    path('contact-us/',contact_us,name='contact')
]