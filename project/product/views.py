from django.shortcuts import render,get_object_or_404
from .models import Product,ProductAttributeValue
from collections import defaultdict

# Create your views here.
def product_detail(request,pk):
    product = get_object_or_404(Product.objects.prefetch_related('product'), id=pk)
    attributes = ProductAttributeValue.objects.filter(product=product)
    grouped_attributes = defaultdict(list)
    for attribute in attributes:
        grouped_attributes[attribute.product_attribute.name].append(attribute.value)
    grouped_attributes = dict(grouped_attributes)
    context = {
        'product': product,
        'images': product.product.all(),
        'grouped_attributes': grouped_attributes
    }
    return render(request,'front_end/product/product_detail.html',context)