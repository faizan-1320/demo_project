from django.db import models
from ..users.models import User
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator

# Create your models here.
class Category(models.Model):
    category_name_regex = RegexValidator(regex=r'^[A-Za-z]+$',message='Enter valid Categoty Name')
    category_name = models.CharField(max_length=100,validators=[category_name_regex],error_messages={'blank': 'Category name is required.'})
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class ProductAttributeValue(models.Model):
    value = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'ProductAttributeValue'
        verbose_name_plural = 'ProductAttributeValues'

class ProductAttribute(models.Model):
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'ProductAttribute'
        verbose_name_plural = 'ProductAttributes'

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    attribute = models.ForeignKey(ProductAttribute,on_delete=models.CASCADE)
    attribute_value = models.ForeignKey(ProductAttributeValue,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

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
        (2,'Redy For Shipment'),
        (3,'Shipped'),
        (4,'Deliverd'),
    )
    payment_status_choice = (
        (1,'SUCCESS'),
        (2,'FAILURE'),
        (3,'PENDING')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    status = models.IntegerField(choices=status_choice,default=1)

    total_amount = models.FloatField(default=None)
    payment_status = models.IntegerField(choices=payment_status_choice,default=3)
    order_id = models.CharField(unique=True,max_length=100,null=True,blank=True,default=None)
    datetime_of_payment = models.DateTimeField(default=timezone.now)

    def save(self,*args,**kwargs):
        if self.order_id is None and self.datetime_of_payment and self.id:
            self.order_id = self.datetime_of_payment.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args,**kwargs)
    
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