"""
Configuration for the Order application.
"""
from django.apps import AppConfig


class OrderConfig(AppConfig):
    """
    AppConfig for the Order app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name =  __name__.rpartition('.')[0]
