"""
Models for the Coupon application.
"""
from datetime import date
from django.db import models
from project.utils import base_model # pylint: disable=E0401

class Coupon(base_model.BaseModel):
    """
    Model representing a coupon with discount details.
    """
    code = models.CharField(
        max_length=150,
        unique=True,
        help_text='Unique coupon code'
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text='Fixed discount amount'
    )
    start_date = models.DateField(
        help_text='Start date of the coupon validity'
    )
    end_date = models.DateField(
        help_text='End date of the coupon validity'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the coupon is active or not'
    )
    is_delete = models.BooleanField(
        default=False,
        help_text='Whether the coupon is deleted or not'
    )

    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta options for CouponModel.
        """
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'

    def __str__(self):
        return str(self.code)
    def is_valid(self):
        """
        Check if the coupon is currently valid.
        """
        return self.is_active and self.start_date <= date.today() <= self.end_date
    def get_discount(self):
        """
        Calculate the discount based on the coupon.
        """
        if not self.is_valid():
            return 0
        discount = 0
        if self.discount_amount > 0:
            discount = self.discount_amount
        return discount
