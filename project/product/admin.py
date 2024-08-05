from django.contrib import admin
from .models import Product,ProductAttribute,ProductAttributeValue,ProductImage,Category

class ProductAttributeAdmin(admin.StackedInline):
    model = ProductAttributeValue

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductAttributeAdmin,ProductImageAdmin]
# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(ProductImage)
admin.site.register(Category)