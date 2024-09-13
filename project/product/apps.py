"""
Configuration for the Product application.
"""
from django.apps import AppConfig


class ProductConfig(AppConfig):
    """
    AppConfig for the Product app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = __name__.rpartition('.')[0]
