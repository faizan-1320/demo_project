"""
Configuration for the Users application.
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    AppConfig for the Users app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = __name__.rpartition('.')[0]
