"""
Configuration for the CustomAdmin application.
"""
from django.apps import AppConfig

class CustomadminConfig(AppConfig):
    """
    AppConfig for the CustomAdmin app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = __name__.rpartition('.')[0]
