from django.shortcuts import render,redirect
from project.users.models import User,Address
from project.product.models import Category,Product,ProductAttribute,ProductAttributeValue,ProductImage,Order,ProductInOrder
from .models import Banner,ContactUs,EmailTemplate
from .forms import BannerForm,CustomFlatPageForm,EmailTemplateForm,OrderStatusForm
from project.coupon.models import Coupon
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from project.utils import custom_required,custom_eamil
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from collections import defaultdict
from django.db.utils import IntegrityError
from django.contrib.auth.decorators import permission_required
from decimal import Decimal, InvalidOperation
from django.contrib.flatpages.models import FlatPage
import re   

####################
# Admin Management #
####################

def adminlogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email)
        errors={}
        if not email:
            errors['email'] = 'Please Enter Email'

        if not password:
            errors['password'] = 'Please Enter Password'

        if not user.exists():
            errors['user_exists'] = 'Account not found'        
        user = authenticate(username=email,password=password)

        if user is None:
            errors['not_admin'] = 'Enter Valid Credentials'
        elif not user.is_superuser and not user.groups.filter(name__in=['inventory manager','order manager']).exists():
            errors['not_admin'] = 'You do not have permission to access this page.'
    
        if any(errors.values()):
            return JsonResponse({'errors':errors})

        login(request, user)
        return JsonResponse({'success': True,'message':'Login Successfully!'})
    return render(request,'admin/authentication/login.html')

def logoutadmin(request):
    logout(request)
    return redirect('adminlogin')

def dashboard(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    user_count = User.objects.filter(is_superuser=False, is_active=True).count()
    product_count = Product.objects.filter(is_active=True,is_delete=False).count()
    category_count = Category.objects.filter(is_active=True,is_delete=False,parent=None).count()
    sub_category_count = Category.objects.filter(is_active=True,is_delete=False,parent=True).count()
    coupon_count = Coupon.objects.filter(is_active=True,is_delete=False).count()
    banner_count = Banner.objects.filter(is_active=True,is_delete=False).count()
    contact = ContactUs.objects.all().count()
    context = {
        'product_count':product_count,
        'user_count':user_count,
        "category_count":category_count,
        "sub_category_count":sub_category_count,
        'coupon_count':coupon_count,
        'banner_count':banner_count,
        'contact_count':contact,
    }
    return render(request,'admin/dashboard.html',context)

###################
# User Management #
###################

@permission_required('users.view_user', raise_exception=True)
def users(request):

    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    search_query = request.GET.get('search','')
    # Filter users to include only active and non-deleted ones
    users = User.objects.filter(
        is_active=True,
        is_delete=False,
        is_superuser=False
    ).filter(
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query) |
        Q(email__icontains=search_query)
    ).prefetch_related('address')

    paginator = Paginator(users,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Calculate the start number for the current page
    start_number = (page_obj.number - 1) * paginator.per_page + 1
    context = {
        'page_obj':page_obj,
        'start_number':start_number,
        'search_query':search_query
    }
    if search_query and not users.exists():
        context['not_found_message'] = 'No users found'
    return render(request, 'admin/users/users.html', context)

@permission_required('users.add_user', raise_exception=True)
def add_users(request):
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    groups = Group.objects.all()
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        groupids = request.POST.getlist('groups[]')

        errors = {}
        
        if not first_name:
            errors['first_name'] = 'Please Enter First Name'
        # Validate first name format
        elif not re.match(r'^[A-Za-z]+$', first_name):
            errors['first_name'] = 'Please Enter Valid First Name (eg :Faizan)'

        if not last_name:
            errors['last_name'] = 'Please Enter Last Name'
        # Validate last name
        elif not re.match(r'^[A-Za-z]+$',last_name):
            errors['last_name'] = 'Please Enter Valid Last Name (eg :Diwan)'
            
        # Validate email
        if not email:
            errors['email'] = 'Please Enter Email Address'
        elif not re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = 'Please Enter Valid Email Address'

        # Validate phone number
        if not phone_number:
            errors['phone_number'] = 'Please Enter Phone Number'
        elif not re.match('^\+?[1-9]\d{1,14}$|^(\(?\d{3}\)?[\s.-]?)?[\s.-]?\d{3}[\s.-]?\d{4}$',phone_number):
            errors['phone_number'] = 'Please Enter valid phone number'
        
        # Validate password
        if not password:
            errors['password'] = 'Please Enter Password'
        elif not re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$',password):
            errors['password'] = 'Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character.'
            
        # Password Match
        if not confirm_password:
            errors['confirm_password'] = 'Please Enter Confirm Password'
        elif password != confirm_password:
            errors['confirm_password'] = 'Password and Confirm password does not mactch'

        if not groupids:
            errors['groupids'] = 'Please Select Group'

        # Check User Exitst or not
        if User.objects.filter(email=email).exists():
            errors['email_exists'] = 'Email already Exists Use another one!'

        if any(errors.values()):
            return JsonResponse({'success': False, 'errors': errors})
            
        try:
            # Create new user without setting password
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number
            )

            # Set the password using set_password method
            new_user.set_password(password)
            new_user.save()

            # Add user to selecetd groups
            for id in groupids:
                group = Group.objects.get(id=int(id))
                new_user.groups.add(group)
            context_email={
                'first_name':first_name,
                'email':email
            }
            custom_eamil.send_custom_mail(to_email=email,context=context_email,template_name='register')

            return JsonResponse({'success': True, 'message': 'User created successfully!'})
        except Exception as e:
            return JsonResponse({'success':False,'errors': {'server':str(e)}})
    context = {
    'groups':groups
    }
    return render(request,'admin/users/add_user.html',context)

@permission_required('users.delete_user', raise_exception=True)
def delete_user(request, pk):
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            messages.error(request, 'User Not Found')
            return redirect('users')
        
        # Set fields and save
        user.is_active = False
        user.is_delete = True
        user.save()
        
        messages.success(request, 'User Deleted Successfully!')
        return redirect('users')
    
    return redirect('users')

@permission_required('users.change_user', raise_exception=True)
def edit_user(request,pk):
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    
    user = User.objects.get(id=pk)
    user_detail = {
        'first_name':user.first_name,
        'last_name':user.last_name,
        'email':user.email,
        'phone_number':user.phone_number
    }
    groups = Group.objects.all()
    user_groups = user.groups.all()
    user_group_ids = user_groups.values_list('id', flat=True)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        groupids = request.POST.getlist('groups[]')

        errors = {}
        
        if not first_name:
            errors['first_name'] = 'Please Enter First Name'
        # Validate first name format
        elif not re.match(r'^[A-Za-z]+$', first_name):
            errors['first_name'] = 'Please Enter Valid First Name (eg :Faizan)'

        if not last_name:
            errors['last_name'] = 'Please Enter Last Name'
        # Validate last name
        elif not re.match(r'^[A-Za-z]+$',last_name):
            errors['last_name'] = 'Please Enter Valid Last Name (eg :Diwan)'
            
        # Validate email
        if not email:
            errors['email'] = 'Please Enter Email Address'
        elif not re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = 'Please Enter Valid Email Address'

        # Validate phone number
        if not phone_number:
            errors['phone_number'] = 'Please Enter Phone Number'
        elif not re.match('^\+?[1-9]\d{1,14}$|^(\(?\d{3}\)?[\s.-]?)?[\s.-]?\d{3}[\s.-]?\d{4}$',phone_number):
            errors['phone_number'] = 'Please Enter valid phone number'

        if any(errors.values()):
            return JsonResponse({'success': False, 'errors': errors})

        try:
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.phone_number=phone_number
            user.save()
            user.groups.clear()
            for id in groupids:
                group = Group.objects.get(id=id)
                user.groups.add(group)

            return JsonResponse({'success': True,'message':'User Update Successfully!'})
        except Exception as e:
            return JsonResponse({'success':False,'errors':{'server':str(e)}})
    context = {
    'groups':groups,
    'user':user,
    'user_group_ids': user_group_ids
    }
    return render(request,'admin/users/edit_user.html',context)

#######################
# Category Management #
#######################

@permission_required('product.view_category', raise_exception=True)
def category(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    
    search_query = request.GET.get('search','')
    category = Category.objects.filter(is_active=True,is_delete=False,category_name__icontains=search_query)
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

@permission_required('product.add_category', raise_exception=True)
def add_category(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':

        category_name = request.POST.get('category_name')

        if not category_name:
            messages.error(request, 'Category name is required.')
            return render(request, 'admin/category/add_category.html')
        
        # Additional validation can go here (e.g., checking if the category already exists)
        if Category.objects.filter(category_name=category_name).exists():
            messages.error(request, 'Category already exists.')
            return render(request, 'admin/category/add_category.html')
        
        category = Category(
            category_name=category_name
        )
        try:
            category.save()
            messages.success(request, 'Category added successfully!')
            return render(request, 'admin/category/add_category.html')  
        except Exception as e:
            messages.error(request, f'Error saving category: {e}')
    
    return render(request, 'admin/category/add_category.html')

@permission_required('product.change_category', raise_exception=True)
def edit_category(request,pk):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category = Category.objects.get(pk=pk)
        category.category_name = category_name
        category.save()
        messages.success(request, 'Category edited successfully')
        return JsonResponse({'success': True, 'message': 'Category edited successfully'})
    return render(request, 'admin/category/edit_category.html')

@permission_required('product.delete_category', raise_exception=True)
def delete_category(request,pk):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        category = Category.objects.get(id=pk)
        # Mark this category and all its sub-categories as deleted
        def mark_as_deleted(cat):
            cat.is_active = False
            cat.is_delete = True
            cat.save()
            # Recursively mark sub-categories
            for sub_cat in cat.category_set.all():
                mark_as_deleted(sub_cat)
        
        mark_as_deleted(category)
        messages.success(request, 'Category Deleted Successfully!')
        return redirect('categories')
    return redirect('categories')

@permission_required('product.delete_category', raise_exception=True)
def add_sub_category(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    category = Category.objects.filter(parent_id=None)
    context = {
    'category':category
    }
    if request.method == 'POST':
        sub_category_name = request.POST.get('sub_category_name')
        parent_id = request.POST.get('parent_id')

        if not sub_category_name:
            messages.error(request, 'Sub Category Name Required')
            return render(request, 'admin/category/add_sub_category.html', context)
        
        if not parent_id:
            messages.error(request, 'Please select a category')
            return render(request, 'admin/category/add_sub_category.html', context)
        
        Category.objects.create(category_name=sub_category_name, parent_id=parent_id)
        messages.success(request, 'Sub Category added successfully')
        return render(request, 'admin/category/add_sub_category.html', context)

    return render(request, 'admin/category/add_sub_category.html',context)

######################
# Product Management #
######################

@permission_required('product.view_product', raise_exception=True)
def product(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    search_query = request.GET.get('search','')
    products = Product.objects.filter(is_active=True, is_delete=False).select_related('category').prefetch_related('product__product', 'products__product_attribute')
    # Apply the search filter only if search_query is not None
    if search_query:
        products = products.filter(name__icontains=search_query)
    paginator = Paginator(products,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1
    # Group attribute values by their attribute names
    attribute_groups = defaultdict(lambda: defaultdict(list))
    
    for product in page_obj:
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
def add_products(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    
    category = Category.objects.all()
    context = {'category': category}

    if request.method == 'POST':
        name = request.POST.get('product_name')
        price = request.POST.get('price')
        category_id = request.POST.get('category_id')
        images = request.FILES.getlist('product_images[]')

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

        if not category_id:
            messages.error(request, 'Please Select Category')
            return render(request, 'admin/product/add_product.html', context)

        if not messages.get_messages(request):  # Proceed if there are no error messages
            try:
                product = Product.objects.create(name=name, price=price, category_id=category_id)
                for image in images:
                    fs = FileSystemStorage(location='media/product_images')
                    filename = fs.save(image.name, image)
                    ProductImage.objects.create(product=product, image='product_images/' + filename)
                messages.success(request, 'Product Added Successfully')
            except IntegrityError:
                messages.error(request, 'Product with this name already exists in the selected category.')
        
        return render(request, 'admin/product/add_product.html', context)

    return render(request, 'admin/product/add_product.html', context)

@permission_required('product.delete_product')
def delete_product(request,pk):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        product = Product.objects.get(id=pk)
        product.is_active = False
        product.is_delete = True
        product.save()
        return redirect('products')
    return render(request,'admin/product/product.html')

@permission_required('product.change_product',raise_exception=True)
def edit_product(request, pk):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    
    product = get_object_or_404(Product, id=pk)
    categories = Category.objects.all()
    product_images = ProductImage.objects.filter(product=product, is_active=True, is_delete=False)
    attribute_values = ProductAttributeValue.objects.filter(product=product)

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

    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        price = request.POST.get('price')
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
        if not category_id:
            messages.error(request, 'Please Select Category')
            return render(request, 'admin/product/edit_product.html', context)
        
        # Update product if there are no validation errors
        if not messages.get_messages(request):
            try:
                # import pdb;pdb.set_trace()
                product.name = product_name
                product.price = price
                product.category_id = category_id
                product.save()

                # Delete attribute values marked for deletion
                deleted_values = []
                if delete_attribute_values:
                    delete_value = ProductAttributeValue.objects.filter(id__in=delete_attribute_values)
                    for av in delete_value:
                        deleted_values.append(av.value)
                    delete_value.delete()

                # Update attribute values
                for attribute_name, values in attribute_values_by_name.items():
                    attribute, created = ProductAttribute.objects.get_or_create(name=attribute_name)
                    existing_values = {av.value for av in ProductAttributeValue.objects.filter(product=product, product_attribute=attribute)}
                    new_values = set(request.POST.getlist(f'attribute_{attribute_name}[]'))

                    # Delete old attribute values not in new values
                    ProductAttributeValue.objects.filter(product=product, product_attribute=attribute).exclude(value__in=new_values).delete()

                    # Add new attribute values not already present
                    for value in new_values - existing_values:
                        if value not in deleted_values and value:
                    
                            ProductAttributeValue.objects.create(
                                product=product,
                                product_attribute=attribute,
                                value=value
                            )

                # Soft delete images
                if images_to_delete:
                    ProductImage.objects.filter(id__in=images_to_delete).update(is_active=False, is_delete=True)
                for image in images:
                    ProductImage.objects.create(product=product, image=image)
            except IntegrityError:
                messages.error(request, 'Product with this name already exists in the selected category') 

            messages.success(request, 'Product Updated Successfully')
                 
        return redirect('products')
    
    return render(request, 'admin/product/edit_product.html', context)

@permission_required('product.add_productattribure', raise_exception=True)
def add_product_attribute(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    
    if request.method == 'POST':
        attribute_name = request.POST.get('attribute_name')
        if not attribute_name:
            messages.error(request,'Enter attribute name')
            return render(request,'admin/product/add_product_attribute.html')
        if ProductAttribute.objects.filter(name=attribute_name).exists():
            messages.error(request, 'Product Attribute already exists.')
            return render(request,'admin/product/add_product_attribute.html')
        
        ProductAttribute.objects.create(name=attribute_name)
        messages.success(request,'Product Attribute Added Successfully')

        return render(request,'admin/product/add_product_attribute.html')
    return render(request,'admin/product/add_product_attribute.html')

@permission_required('product.add_productattributevalue', raise_exception=True)
def add_product_attribute_value(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    product_attribute = ProductAttribute.objects.all()
    product = Product.objects.all()
    
    context ={
        'product_attribute':product_attribute,
        'product':product
    }   
    if request.method == 'POST':
        product_attribute_value = request.POST.get('product_attribute_value')
        product_id = request.POST.get('product_id')
        product_attribute_id = request.POST.get('product_attribute_id')

        if not product_attribute_value:
            messages.error(request,'Product attribute value is required')
            return render(request,'admin/product/add_product_attribute_value.html',context)
        if not product_attribute_id:
            messages.error(request,'Please Select Product Attribute')
            return render(request,'admin/product/add_product_attribute_value.html',context)
        try:
            ProductAttributeValue.objects.create(value=product_attribute_value,product_attribute_id=product_attribute_id,product_id=product_id)
            messages.success(request,'Product Attribute added successfully')
        except IntegrityError:
            messages.error(request,'Attribute value already exists in Product')
            return render(request,'admin/product/add_product_attribute_value.html',context)
    return render(request,'admin/product/add_product_attribute_value.html',context)

#####################
# Banner Management #
#####################

@permission_required('customadmin.view_banner',raise_exception=True)
def banner(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    banner = Banner.objects.filter(is_active=True,is_delete=False)
    paginator = Paginator(banner,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1

    context = {
        'page_obj':page_obj,
        'start_number':start_number
    }
    return render(request,'admin/banner/banner.html',context)

@permission_required('customadmin.add_banner', raise_exception=True)
def add_banner(request):
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner added successfully')
            return redirect('banners')
    else:
        form = BannerForm()

    return render(request, 'admin/banner/add_banner.html', {'form': form})

@permission_required('customadmin.delete_banner',raise_exception=True)
def delete_banner(request,pk):
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        banner = Banner.objects.get(id=pk)
        banner.is_active = False
        banner.is_delete = True
        banner.save()
        return redirect('banners')
    return render(request,'admin/banner/banner.html')

@permission_required('customadmin.change_banner',raise_exception=True)
def edit_banner(request, pk):
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    banner = get_object_or_404(Banner, id=pk)
    if request.method == 'POST':
        # import pdb;pdb.set_trace()
        form = BannerForm(request.POST, request.FILES, instance=banner)
        print('form: ', form)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner updated successfully')
            return redirect('banners')
    else:
        form = BannerForm(instance=banner)

    return render(request, 'admin/banner/edit_banner.html', {'form': form, 'banner': banner})

#########################
# Contact US Management #
#########################

@permission_required('customadmin.view_contact_us',raise_exception=True)
def contact_us(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    search_query = request.GET.get('search','')
    contact = ContactUs.objects.filter(subject__icontains=search_query)
    paginator = Paginator(contact,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1

    context = {
        'page_obj':page_obj,
        'start_number':start_number,
        'search_query':search_query
    }
    if search_query and not contact.exists():
        context['message_not_found'] = 'Not Contact Us found'
    return render(request,'admin/contact_us/contact_us.html',context)

@permission_required('customadmin.change_contact_us',raise_exception=True)
def contact_us_detail(request, pk):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    contact = get_object_or_404(ContactUs, pk=pk)

    if request.method == 'POST':
        reply = request.POST.get('admin_reply')
        if reply and not contact.is_replied:
            contact.admin_reply = reply
            contact.is_replied = True
            contact.save()
            return redirect('contact-us')
    return render(request, 'admin/contact_us/contact_us_detail.html', {'contact': contact})

##################
# CMS Management #
##################

@permission_required('flatpages.view_flat_page',raise_exception=True)
def flatpage_list(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    flatpages = FlatPage.objects.all()
    return render(request, 'admin/cms/flatpage.html', {'flatpages': flatpages})

@permission_required('flatpages.add_flat_page',raise_exception=True)
def add_flatpage(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        form = CustomFlatPageForm(request.POST)
        if form.is_valid():
            flatpage = form.save()
            return redirect('cms')
    else:
        form = CustomFlatPageForm()
    return render(request,'admin/cms/add_flatpage.html',{'form':form})

@permission_required('flatpages.change_flat_page',raise_exception=True)
def edit_flatpage(request,pk):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    flatpage = get_object_or_404(FlatPage, id=pk)
    if request.method == 'POST':
        form = CustomFlatPageForm(request.POST,instance=flatpage)
        if form.is_valid():
            form.save()
            return redirect('cms')
    else:
        form = CustomFlatPageForm(instance=flatpage)
    return render(request,'admin/cms/edit_flatpage.html',{'form':form,'flatpage':flatpage})

@permission_required('flatpages.delete_flat_page',raise_exception=True)
def delete_flatpage(request,pk):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    flatpage =  FlatPage.objects.filter(id=pk)
    if request.method == 'POST':
        flatpage.delete()
        return redirect('cms')
    return render(request,'admin/cms/flatpage.html')

#############################
# Email Templage Management #
#############################

@permission_required('customadmin.view_email_template',raise_exception=True)
def email_template(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    
    email_templates = EmailTemplate.objects.filter(is_active=True)
    if not email_templates.exists():
        email_err = 'No email templates available.'
        return render(request, 'admin/email_template/email_template.html', {'email_err': email_err})
    
    return render(request, 'admin/email_template/email_template.html', {'email_templates': email_templates})

@permission_required('customadmin.add_email_template',raise_exception=True)
def add_template(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('emails')
    else:
        form = EmailTemplateForm()
    return render(request,'admin/email_template/add_email_template.html',{'form':form})

@permission_required('customadmin.change_email_template',raise_exception=True)
def edit_email_template(request, pk):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            return redirect('emails')
    else:
        form = EmailTemplateForm(instance=template)
    return render(request, 'admin/email_template/edit_email_template.html', {'form': form})

@permission_required('customadmin.delete_email_template',raise_exception=True)
def delete_email_template(request, pk):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        template.delete()
        return redirect('emails')
    return render(request, 'admin/email_template/email_template.html', {'template': template})

####################
# Order Management #
####################

@permission_required('product.view_order',raise_exception=True)
def order(request):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    search_query = request.GET.get('search','')
    orders = Order.objects.filter(order_id__icontains=search_query)
    paginator = Paginator(orders,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1

    context = {
        'page_obj':page_obj,
        'start_number':start_number,
        'search_query':search_query
    }
    if search_query and not orders.exists():
        context['message_not_found'] = 'Not order found'
    return render(request, 'admin/orders/orders.html', context)

@permission_required('product.change_order',raise_exception=True)
def order_detail(request, pk):
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')

    # Fetch the order details
    order = get_object_or_404(Order, id=pk)
    products_in_order = ProductInOrder.objects.filter(order=order)
    customer_address = Address.objects.filter(user=order.user, is_active=True).first()

    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            
            context_email = {
                    'order_id': order.order_id,
                    'datetime_of_payment':order.datetime_of_payment,
                    'shipping_method':order.shipping_method,
                    'payment_status':order.payment_status,
                    'total_amount':order.total_amount,
                    'first_name': order.user.first_name,
                    'order_status': dict(Order.status_choice).get(new_status, 'Unknown'),
                    'products': products_in_order,
                    'customer_address': customer_address,
                    'is_cash_on_delivery':order.is_cash_on_delivery
                }
            try:
                custom_eamil.send_custom_mail(
                    to_email=order.user.email,
                    context=context_email,
                    template_name='order_status'
                )
            except Exception as e:
                print('Error sending email:', e)
    
            form.save()
            messages.success(request, 'Order status updated successfully.')
            return redirect('order-detail', pk=pk)
    else:
        form = OrderStatusForm(instance=order)

    context = {
        'order': order,
        'products_in_order': products_in_order,
        'customer_address': customer_address,
        'form': form
    }

    return render(request, 'admin/orders/order_detail.html', context)
    