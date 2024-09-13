"""
URL configurations for the custom admin panel. 
Includes routes for managing users, categories, products, banners, 
contact us entries, CMS pages, email templates, orders, and newsletters.
"""

from django.urls import path
from .views import (
    adminlogin, logoutadmin, dashboard, users, add_users, delete_user, edit_user,
    banner, add_banner, delete_banner,
    edit_banner, contact_us, contact_us_detail, flatpage_list, add_flatpage,
    edit_flatpage, delete_flatpage, email_template, add_template, edit_email_template,
    delete_email_template, news_letter
)

urlpatterns = [
    path('', adminlogin, name='adminlogin'),
    path('logout-admin/', logoutadmin, name='logout-admin'),
    path('dashboard/', dashboard, name='dashboard'),
    # User URL
    path('users/', users, name='users'),
    path('users/add/', add_users, name='add-user'),
    path('users/<int:pk>/delete/', delete_user, name='user-delete'),
    path('users/<int:pk>/edit/', edit_user, name='user-edit'),
    # Banner URL
    path('banners/', banner, name='banners'),
    path('banners/add/', add_banner, name='add-banner'),
    path('banners/<int:pk>/delete/', delete_banner, name='delete-banner'),
    path('banners/<int:pk>/edit/', edit_banner, name='edit-banner'),
    # Contact_US URL
    path('contact-us/', contact_us, name='contact-us'),
    path('contact-us/<int:pk>/details', contact_us_detail, name='contact-us-details'),
    # CMS URL
    path('cms/', flatpage_list, name='cms'),
    path('cms/add/', add_flatpage, name='add-flatpage'),
    path('cms/<int:pk>/edit', edit_flatpage, name='edit-flatpage'),
    path('cms/<int:pk>/delete', delete_flatpage, name='delete-flatpage'),
    # Email URL
    path('emails/', email_template, name='emails'),
    path('emails/add', add_template, name='email-add'),
    path('emails/<int:pk>/edit/', edit_email_template, name='edit-email'),
    path('emails/<int:pk>/delete/', delete_email_template, name='delete-email'),
    # News Letter
    path('news/letter/', news_letter, name='news-letter'),
]
