"""
Admin configuration for the Product model.
"""
from django.contrib import admin
from .models import Product,ProductAttribute,ProductAttributeValue,ProductImage,Category

class ProductAttributeAdmin(admin.StackedInline):
    """
    Admin configuration for the ProductAttributeAdmin model.
    """
    model = ProductAttributeValue

class ProductImageAdmin(admin.StackedInline):
    """
    Admin configuration for the ProductImageAdmin model.
    """
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ProductAdmin model.
    """
    inlines = [ProductAttributeAdmin,ProductImageAdmin]
# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(ProductImage)
admin.site.register(Category)
