"""
Admin configuration for the CustomAdmin model.
"""
from django.contrib import admin
from .models import Order

# Register your models here.
admin.site.register(Order)
