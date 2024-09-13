# pylint: disable=R0801
"""
Views for the CustomAdmin.

This module contains views for listing, creating, editing, and deleting CustomAdmin.
"""
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.core.files.storage import FileSystemStorage
from django.db.utils import IntegrityError
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from project.utils import custom_required #pylint: disable=E0401
from .models import (
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
    Category)
from .forms import ProductAttributeForm


######################
# Product Management #
######################

@permission_required('product.view_product', raise_exception=True)
def product(request):
    """
    Display a list.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    search_query = request.GET.get('q','')
    products = Product.objects.filter( # pylint: disable=E1101
        is_active=True,
        is_delete=False).select_related(
        'category').prefetch_related(
        'product__product',
        'products__product_attribute')
    # Apply the search filter only if search_query is not None
    if search_query:
        products = products.filter(name__icontains=search_query)
    paginator = Paginator(products,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1
    # Group attribute values by their attribute names
    attribute_groups = defaultdict(lambda: defaultdict(list))
    for product in page_obj: #pylint: disable=W0621
        for attribute_value in product.products.all():
            attribute_name = attribute_value.product_attribute.name
            attribute_groups[product.id][attribute_name].append(attribute_value.value)
    context = {
        'page_obj':page_obj,
        'attribute_groups': attribute_groups,
        'start_number':start_number,
        'search_query':search_query
    }
    if search_query and not products.exists():
        context['not_found_message'] = 'No products found'
    return render(request,'admin/product/product.html',context)

@permission_required('product.add_product', raise_exception=True)
def add_products(request): #pylint: disable=R0914,R0911,R0912
    """
    Handle the creation.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    category = Category.objects.filter(is_active=True,is_delete=False) # pylint: disable=W0621,E1101
    product_attribute = ProductAttribute.objects.all() # pylint: disable=W0621,E1101
    context = {'category': category,
               'product_attribute':product_attribute}

    if request.method == 'POST':
        name = request.POST.get('product_name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        category_id = request.POST.get('category_id')
        images = request.FILES.getlist('product_images[]')
        product_attribute_ids = request.POST.getlist('product_attribute_id')
        product_attribute_values = request.POST.getlist('product_attribute_value')

        # Validate the inputs
        if not name:
            messages.error(request, 'Product Name is required')
        elif not price:
            messages.error(request, 'Product Price is required')
        else:
            try:
                price = Decimal(price)
                if price < 0:
                    raise InvalidOperation
            except InvalidOperation:
                messages.error(request, 'Please enter a valid positive number for the price')
                return render(request, 'admin/product/add_product.html', context)

        if not quantity:
            messages.error(request, 'Product quantity is required')
        else:
            try:
                quantity = Decimal(quantity)
                if quantity < 0:
                    raise InvalidOperation
            except InvalidOperation:
                messages.error(request, 'Please enter a valid positive number for the quantity')
                return render(request, 'admin/product/add_product.html', context)

        if not category_id:
            messages.error(request, 'Please Select Category')
            return render(request, 'admin/product/add_product.html', context)

        for attribute_value in product_attribute_values:
            if not attribute_value.strip():
                messages.error(request, 'Each attribute must have a corresponding value')
                return render(request, 'admin/product/add_product.html', context)
        if not product_attribute_ids or not product_attribute_values:
            messages.error(request, 'Product attributes and values are required')
            return render(request, 'admin/product/add_product.html', context)
        if not messages.get_messages(request):  # Proceed if there are no error messages
            try:
                # Create the product
                product = Product.objects.create( # pylint: disable=W0621,E1101
                    name=name,
                    price=price,
                    quantity=quantity,
                    category_id=category_id
                )

                # Create product attribute values
                for attribute_id, attribute_value in zip(
                    product_attribute_ids,
                    product_attribute_values
                ):
                    ProductAttributeValue.objects.create( # pylint: disable=E1101
                        value=attribute_value,
                        product_attribute_id=attribute_id,
                        product=product
                    )

                for image in images:
                    fs = FileSystemStorage(location='media/product_images')
                    filename = fs.save(image.name, image)
                    ProductImage.objects.create(product=product, image='product_images/' + filename) # pylint: disable=E1101
                messages.success(request, 'Product Added Successfully')
            except IntegrityError:
                messages.error(request,
                'Product with this name already exists in the selected category.')        
        return render(request, 'admin/product/add_product.html', context)

    return render(request, 'admin/product/add_product.html', context)

@permission_required('product.delete_product')
def delete_product(request,pk):
    """
    Handle the deletion.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        product = Product.objects.get(id=pk) # pylint: disable=W0621,E1101
        product.is_active = False
        product.is_delete = True
        product.save()
        return redirect('products')
    return render(request,'admin/product/product.html')

@permission_required('product.change_product',raise_exception=True)
def edit_product(request, pk): # pylint: disable=R0914,R0912,R0915
    """
    Handle the editing.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    product = get_object_or_404(Product, id=pk) # pylint: disable=W0621
    categories = Category.objects.all() # pylint: disable=E1101
    product_images = ProductImage.objects.filter(product=product, is_active=True, is_delete=False) # pylint: disable=E1101
    attribute_values = ProductAttributeValue.objects.filter(product=product) # pylint: disable=E1101

    # Group attribute values by attribute name
    attribute_values_by_name = defaultdict(list)
    for av in attribute_values:
        attribute_values_by_name[av.product_attribute.name].append({
            'id': av.id,
            'value': av.value
        })
    context = {
        'product': product,
        'categories': categories,
        'product_images': product_images,
        'attribute_values': attribute_values,
        'attribute_values_by_name': dict(attribute_values_by_name)
    }

    if request.method == 'POST':# pylint: disable=R1702
        product_name = request.POST.get('product_name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        category_id = request.POST.get('category_id')
        images_to_delete = request.POST.getlist('images_to_delete')
        images = request.FILES.getlist('product_images[]')
        delete_attribute_values = request.POST.getlist('delete_attribute_values')

        # Form validation
        if not product_name:
            messages.error(request, 'Product Name is required')
        if not price:
            messages.error(request, 'Price is required')
        else:
            try:
                price = Decimal(price)
                if price < 0:
                    raise InvalidOperation
            except InvalidOperation:
                messages.error(request, 'Please enter a valid positive number for the price')
                return render(request, 'admin/product/edit_product.html', context)
        if not quantity:
            messages.error(request, 'quantity is required')
        else:
            try:
                quantity = Decimal(quantity)
                if quantity < 0:
                    raise InvalidOperation
            except InvalidOperation:
                messages.error(request, 'Please enter a valid positive number for the quantity')
                return render(request, 'admin/product/edit_product.html', context)
        if not category_id:
            messages.error(request, 'Please Select Category')
            return render(request, 'admin/product/edit_product.html', context)
        # Update product if there are no validation errors
        if not messages.get_messages(request):
            try:
                # import pdb;pdb.set_trace()
                product.name = product_name
                product.price = price
                product.quantity = quantity
                product.category_id = category_id
                product.save()

                # Delete attribute values marked for deletion
                deleted_values = []
                if delete_attribute_values:
                    delete_value = ProductAttributeValue.objects.filter( # pylint: disable=E1101
                        id__in=delete_attribute_values)
                    for av in delete_value:
                        deleted_values.append(av.value)
                    delete_value.delete()
                # Update attribute values
                for attribute_name, values in attribute_values_by_name.items():# pylint: disable=W0612
                    attribute, created = ProductAttribute.objects.get_or_create(name=attribute_name) # pylint: disable=E1101,W0612
                    existing_values = {av.value for av in ProductAttributeValue.objects.filter( # pylint: disable=E1101
                    product=product, product_attribute=attribute)}
                    new_values = set(request.POST.getlist(f'attribute_{attribute_name}[]'))

                    # Delete old attribute values not in new values
                    ProductAttributeValue.objects.filter( # pylint: disable=E1101
                    product=product, product_attribute=attribute).exclude(
                    value__in=new_values).delete()
                    # Add new attribute values not already present
                    for value in new_values - existing_values:
                        if value not in deleted_values and value:
                            ProductAttributeValue.objects.create( # pylint: disable=E1101
                                product=product,
                                product_attribute=attribute,
                                value=value
                            )
                # Soft delete images
                if images_to_delete:
                    ProductImage.objects.filter(id__in=images_to_delete).delete() # pylint: disable=E1101
                for image in images:
                    ProductImage.objects.create(product=product, image=image) # pylint: disable=E1101
            except IntegrityError:
                messages.error(request,
            'Product with this name already exists in the selected category')

            messages.success(request, 'Product Updated Successfully')

        return redirect('products')

    return render(request, 'admin/product/edit_product.html', context)

@permission_required('product.view_productattribute',raise_exception=True)
def product_attribute(request):
    """
    Display a list.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    product_attribute_data = ProductAttribute.objects.filter(is_active=True,is_delete=False) # pylint: disable=E1101
    search_query = request.GET.get('search_query','')
    if search_query:
        product_attribute_data = ProductAttribute.objects.filter( # pylint: disable=E1101
        is_active=True,is_delete=False,name__icontains=search_query)
    paginator = Paginator(product_attribute_data,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1
    context = {
        'page_obj':page_obj,
        'start_number':start_number,
        'search_query':search_query,
    }
    return render(request,'admin/product/prduct_attribute.html',context)

@permission_required('product.add_productattribute', raise_exception=True)
def add_product_attribute(request):
    """
    Handle the creation.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        attribute_name = request.POST.get('attribute_name')
        if not attribute_name:
            messages.error(request,'Enter attribute name')
            return render(request,'admin/product/add_product_attribute.html')
        if ProductAttribute.objects.filter(name=attribute_name).exists(): # pylint: disable=E1101
            messages.error(request, 'Product Attribute already exists.')
            return render(request,'admin/product/add_product_attribute.html')
        ProductAttribute.objects.create(name=attribute_name) # pylint: disable=E1101
        messages.success(request,'Product Attribute Added Successfully')

        return render(request,'admin/product/add_product_attribute.html')
    return render(request,'admin/product/add_product_attribute.html')

@permission_required('product.change_productattribute',raise_exception=True)
def edit_product_attribute(request,pk):
    """
    Handle the editing.
    """
    attribute = ProductAttribute.objects.get(id=pk) # pylint: disable=E1101
    if request.method == 'POST':
        form = ProductAttributeForm(request.POST,instance=attribute)
        if form.is_valid(): # pylint: disable=R1705
            form.save()
            messages.success(request,'Attribute Update successfully')
            return redirect('product-attribute')
        else:
            messages.error(request,'Somthing went wrong')
    else:
        form = ProductAttributeForm(instance=attribute)
    return render(request,'admin/product/edit_product_attribute.html',{'form':form})

@permission_required('product.delete_productattribute',raise_exception=True)
def delete_product_attribute(request,pk):
    """
    Handle the deletion.
    """
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        delete_attribute = ProductAttribute.objects.get(id=pk) # pylint: disable=E1101
        delete_attribute.is_active = False
        delete_attribute.is_delete = True
        delete_attribute.save()
        messages.success(request,'Attribute delete successfully')
        return redirect('product-attribute')
    return render(request,'admin/product/product_attribute.html')

#######################
# Category Management #
#######################

@permission_required('product.view_category', raise_exception=True)
def category(request):
    """
    Display a list.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    search_query = request.GET.get('search','')
    category = Category.objects.filter( # pylint: disable=W0621,E1101
        is_active=True,
        is_delete=False,
        category_name__icontains=search_query)
    paginator = Paginator(category,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1
    context = {
    'page_obj':page_obj,
    'start_number':start_number,
    'search_query':search_query
    }
    if search_query and not category.exists():
        context['not_found_message'] = 'No Categorys found'
    return render(request,'admin/category/category.html',context)

@permission_required('product.change_category', raise_exception=True)
def edit_category(request,pk):
    """
    Handle the editing.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category = Category.objects.get(pk=pk) # pylint: disable=W0621,E1101
        category.category_name = category_name
        category.save()
        return JsonResponse({'success': True, 'message': 'Category updated successfully'})
    return render(request, 'admin/category/edit_category.html')

@permission_required('product.delete_category', raise_exception=True)
def delete_category(request,pk):
    """
    Handle the deletion.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        category = Category.objects.get(id=pk) # pylint: disable=W0621,E1101
        def hard_delete(cat):
            # First, delete all sub-categories
            for sub_cat in cat.subcategories.all():
                hard_delete(sub_cat)
            # Then, delete the category itself
            cat.delete()
        hard_delete(category)
        messages.success(request, 'Category Deleted Successfully!')
        return redirect('categories')
    return redirect('categories')

@permission_required('product.delete_category', raise_exception=True)
def add_category(request):
    """
    Handle the creation.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    category = Category.objects.filter() # pylint: disable=W0621,E1101
    context = {
    'category':category
    }
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        parent_id = request.POST.get('parent_id')

        if not category_name:
            messages.error(request, 'Category Name Required')
            return render(request, 'admin/category/add_category.html', context)
        Category.objects.create(category_name=category_name, parent_id=parent_id) # pylint: disable=E1101
        messages.success(request, 'Sub Category added successfully')
        return render(request, 'admin/category/add_category.html', context)

    return render(request, 'admin/category/add_category.html',context)
