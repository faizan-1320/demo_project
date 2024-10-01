# pylint: disable=R0801
"""
This module contains models for the custom admin application, including
Category, Product,ProductAttribute,ProductAttributeValue,Rating,Review models.
"""
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator

CATEGORY_DELIMITER = " / "

# Create your models here.
class Category(models.Model):
    """
    Model representing a Category for display.
    """
    category_name_regex = RegexValidator(regex=r'^[A-Za-z]+$',message='Enter valid Categoty Name')
    category_name = models.CharField(
    max_length=100,validators=[category_name_regex],
    error_messages={'blank': 'Category name is required.'})
    parent = models.ForeignKey(
    'self', blank=True, 
    null=True, on_delete=models.CASCADE,related_name='subcategories')
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    @property
    def full_path(self):
        """
        Representing a Ful path category for display.
        """
        comp = [self.category_name]
        parent_cat = self.parent

        while parent_cat is not None:
            comp.insert(0, parent_cat.category_name) # pylint: disable=E1101
            parent_cat = parent_cat.parent # pylint: disable=E1101
        return CATEGORY_DELIMITER.join(comp)

    @property
    def has_subcategories(self):
        """
        Representing a Subcategory.
        """
        return self.subcategories.exists() # pylint: disable=E1101

    def __str__(self):
        return str(self.category_name)

    class Meta: # pylint: disable=R0903
        """
        Meta model
        """
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Product(models.Model):
    """
    Model representing a Product for display.
    """
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    quantity = models.PositiveIntegerField(null=True,blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='categories')
    is_features = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.name)
    class Meta: # pylint: disable=R0903
        """Meta class"""
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        unique_together = ('name', 'category')

class ProductAttribute(models.Model):
    """
    Model representing a ProductAttribute for display.
    """
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.name)
    class Meta: # pylint: disable=R0903
        """Meta Class"""
        verbose_name = 'ProductAttribute'
        verbose_name_plural = 'ProductAttributes'

class ProductAttributeValue(models.Model):
    """
    Model representing a ProductAttributeValue for display.
    """
    value = models.CharField(max_length=150)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='products')
    product_attribute = models.ForeignKey(
    ProductAttribute,on_delete=models.CASCADE,related_name='product_attribute')
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.value)
    class Meta: # pylint: disable=R0903
        """Meta Class"""
        verbose_name = 'ProductAttributeValue'
        verbose_name_plural = 'ProductAttributeValues'
        unique_together = ('value','product')

class ProductImage(models.Model):
    """
    Model representing a ProductImage for display.
    """
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product')
    image = models.ImageField(upload_to='product_images/')
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return str(f'{self.product.name} - {self.id}') # pylint: disable=E1101

    class Meta: # pylint: disable=R0903
        """Meta Class"""
        verbose_name = 'ProductImage'
        verbose_name_plural = 'ProductImages'

class Review(models.Model):
    """
    Model representing a Review for display.
    """
    message = models.TextField()
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta: # pylint: disable=R0903
        """Meta Class"""
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return str(f"Review for {self.product.name}")

class Rating(models.Model):
    """
    Model representing a Rating for display.
    """
    rating = models.FloatField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta: # pylint: disable=R0903
        """Meta Class"""
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'

    def __str__(self): # pylint: disable=E1101
        return str(f"{self.rating} stars for {self.product.name} by {self.user.username}") # pylint: disable=E1101

    def save(self, *args, **kwargs):
        if self.rating < 1 or self.rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        super().save(*args, **kwargs)
