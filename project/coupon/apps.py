"""
Configuration for the Coupon application.
"""
from django.apps import AppConfig

class CouponConfig(AppConfig):
    """
    AppConfig for the Coupon app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = __name__.rpartition('.')[0]
