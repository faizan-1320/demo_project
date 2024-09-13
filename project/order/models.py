"""
This module contains models for the custom admin application, including
Order, ProductInOrder models.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from project.product.models import Product # pylint: disable=E0401
from project.users.models import Address # pylint: disable=E0401
from project.coupon.models import Coupon # pylint: disable=E0401


# Create your models here.
class Order(models.Model):
    """
    Model representing a Order for display.
    """
    status_choice = (
        (1,'Not Packed'),
        (2,'Ready For Shipment'),
        (3,'Shipped'),
        (4,'Deliverd'),
    )
    payment_status_choice = (
        (1, 'SUCCESS'),
        (2, 'FAILURE'),
        (3, 'PENDING'),
        (4, 'REFUNDED'),
        (5, 'DISPUTED'),
        (6, 'CASH_ON_DELIVERY')
    )
    shipping_method_choice = (
        (1, 'Standard Shipping'),
        (2, 'Express Shipping'),
        (3, 'Overnight Shipping'),
        (4, 'Pickup'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    status = models.IntegerField(choices=status_choice,default=1)
    address = models.ForeignKey(
    Address,
    on_delete=models.CASCADE,
    related_name='order_address', null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    payment_status = models.IntegerField(choices=payment_status_choice,default=3)
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    datetime_of_payment = models.DateTimeField(default=timezone.now)
    is_cash_on_delivery = models.BooleanField(default=False)
    shipping_method = models.IntegerField(choices=shipping_method_choice, default=1)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if self.payment_status == 6:
            self.is_cash_on_delivery = True
        else:
            self.is_cash_on_delivery = False

        if not self.order_id:
            self.order_id = self.datetime_of_payment.strftime( # pylint: disable=E1101
            'PAY2ME%Y%m%dODR') + str(uuid.uuid4().hex[:6]).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.email + " " + str(self.id) # pylint: disable=E1101

class ProductInOrder(models.Model):
    """
    Model representing a ProductInOrder for display.
    """
    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta options for ProductInOrder.
        """
        unique_together = (('order', 'product'),)
    order = models.ForeignKey(Order, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()

    class Meta: # pylint: disable=too-few-public-methods,E0102
        """
        Meta options for ProductInOrder.
        """
        verbose_name = 'ProductInOrder'
        verbose_name_plural = 'ProductInOrders'
