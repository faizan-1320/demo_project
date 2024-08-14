from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator
import uuid

CATEGORY_DELIMITER = " / "

# Create your models here.
class Category(models.Model):
    category_name_regex = RegexValidator(regex=r'^[A-Za-z]+$',message='Enter valid Categoty Name')
    category_name = models.CharField(max_length=100,validators=[category_name_regex],error_messages={'blank': 'Category name is required.'})
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    @property
    def full_path(self):
        comp = [self.category_name]
        parent_cat = self.parent

        while parent_cat is not None:
            comp.insert(0, parent_cat.category_name)
            parent_cat = parent_cat.parent
        return CATEGORY_DELIMITER.join(comp)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='categories')
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        unique_together = ('name', 'category')

class ProductAttribute(models.Model):
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'ProductAttribute'
        verbose_name_plural = 'ProductAttributes'
        
class ProductAttributeValue(models.Model):
    value = models.CharField(max_length=150)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='products')
    product_attribute = models.ForeignKey(ProductAttribute,on_delete=models.CASCADE,related_name='product_attribute')
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.value
    class Meta:
        verbose_name = 'ProductAttributeValue'
        verbose_name_plural = 'ProductAttributeValues'
        unique_together = ('value','product')

class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product')
    image = models.ImageField(upload_to='product_images/')
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'ProductImage'
        verbose_name_plural = 'ProductImages'

class Comment(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    number = models.IntegerField()
    message = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)   
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

class Rating(models.Model):
    rating = models.FloatField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'

class CartManager(models.Manager):
    def create_cart(self,user):
        cart = self.create(user=user)
        return cart

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    objects = CartManager()

class ProductInCart(models.Model):
    class Meta:
        unique_together = (('cart','product'))
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

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