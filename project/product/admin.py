from django.contrib import admin
from .models import Product,ProductAttribute,ProductAttributeValue,ProductImage,Category
# Register your models here.
admin.site.register(Product)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(ProductImage)
admin.site.register(Category)