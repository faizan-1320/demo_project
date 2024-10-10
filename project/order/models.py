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
from project.utils.base_model import BaseModel # pylint: disable=E0401


# Create your models here.
from datetime import timedelta

class Order(BaseModel):
    """
    Model representing an Order for display.
    """
    status_choice = (
        (1, 'Not Packed'),
        (2, 'Ready For Shipment'),
        (3, 'Shipped'),
        (4, 'Delivered'),
    )
    payment_status_choice = (
        (1, 'SUCCESS'),
        (2, 'FAILURE'),
        (3, 'PENDING'),
        (4, 'REFUNDED'),
        (5, 'DISPUTED'),
    )
    shipping_method_choice = (
        (1, 'Standard Shipping'),
        (2, 'Express Shipping'),
        (3, 'Overnight Shipping'),
        (4, 'Pickup'),
    )

    payment_method_choice = (
        (1, 'Paypal'),
        (2, 'Cash on Delivery'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.IntegerField(choices=status_choice, default=1)
    billing_address = models.TextField(null=True, blank=True)
    shipping_address = models.TextField(null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    payment_method = models.IntegerField(choices=payment_method_choice, default=1)
    payment_status = models.IntegerField(choices=payment_status_choice, default=3)
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    datetime_of_payment = models.DateTimeField(default=timezone.now)
    shipping_method = models.IntegerField(choices=shipping_method_choice, default=1)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.FloatField(default=0)
    paypal_payment_id = models.CharField(max_length=255, null=True, blank=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """Save Function"""

        if not self.order_id:
            self.order_id = self.datetime_of_payment.strftime( # pylint: disable=E1101
            'PAY2ME%Y%m%dODR') + str(uuid.uuid4().hex[:6]).upper()

        # Calculate estimated delivery date based on shipping method
        if self.status == 3:  # Order is marked as 'Shipped'
            if self.shipping_method == 1:
                self.estimated_delivery_date = timezone.now().date() + timedelta(days=5)  # Standard Shipping
            elif self.shipping_method == 2:
                self.estimated_delivery_date = timezone.now().date() + timedelta(days=2)  # Express Shipping
            elif self.shipping_method == 3:
                self.estimated_delivery_date = timezone.now().date() + timedelta(days=1)  # Overnight Shipping
        super().save(*args, **kwargs)

    def get_shipping_method_display(self):
        return dict(self.__class__.shipping_method_choice).get(self.shipping_method, "Unknown Method")

    def get_payment_status_display(self):
        return dict(self.__class__.payment_status_choice).get(self.payment_status, "Unknown Status")
    
    def get_payment_method_display(self):
        return dict(self.__class__.payment_method_choice).get(self.payment_method, "Unknown Status")
    
    def get_order_status_display(self):
        return dict(self.__class__.status_choice).get(self.status, "Unknown Status")
    
    def __str__(self):
        return f"{self.user.email} {self.order_id}"

class ProductInOrder(models.Model):
    """
    Model representing a ProductInOrder for display.
    """
    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta options for ProductInOrder.
        """
        unique_together = (('order', 'product'),)
    order = models.ForeignKey(Order, on_delete = models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()

    class Meta: # pylint: disable=too-few-public-methods,E0102
        """
        Meta options for ProductInOrder.
        """
        verbose_name = 'ProductInOrder'
        verbose_name_plural = 'ProductInOrders'
