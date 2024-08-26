import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from project.product.models import Product


# Create your models here.
class Order(models.Model):
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

    total_amount = models.FloatField(default=0.0)
    payment_status = models.IntegerField(choices=payment_status_choice,default=3)
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    datetime_of_payment = models.DateTimeField(default=timezone.now)
    is_cash_on_delivery = models.BooleanField(default=False)
    shipping_method = models.IntegerField(choices=shipping_method_choice, default=1)

    def save(self, *args, **kwargs):
        if self.payment_status == 6:
            self.is_cash_on_delivery = True
        else:
            self.is_cash_on_delivery = False

        if not self.order_id:
            self.order_id = self.datetime_of_payment.strftime('PAY2ME%Y%m%dODR') + str(uuid.uuid4().hex[:6]).upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.user.email + " " + str(self.id)

class ProductInOrder(models.Model):
    class Meta:
        unique_together = (('order', 'product'),)
    order = models.ForeignKey(Order, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()

    class Meta:
        verbose_name = 'ProductInOrder'
        verbose_name_plural = 'ProductInOrders'