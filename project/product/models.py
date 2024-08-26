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
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE,related_name='subcategories')
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

    @property
    def has_subcategories(self):
        return self.subcategories.exists()
    
    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    quantity = models.PositiveIntegerField(null=True,blank=True)
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

    def __str__(self) -> str:
        return f'{self.product.name} - {self.id}'

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
