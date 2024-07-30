from django.shortcuts import render,redirect
from project.users.models import User
from project.product.models import Category,Product,ProductAttribute,ProductAttributeValue,ProductImage
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from project.utils.custom_required import check_login_admin,role_manage,role_required
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
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
    if not check_login_admin(request.user):
        return redirect('adminlogin')
    user_count = User.objects.filter(is_superuser=False, is_active=True).count()
    role = role_manage(request.user)
    context = {
        'user_role':role,
        'user_count':user_count
    }
    return render(request,'admin/dashboard.html',context)

###################
# User Management #
###################

@csrf_exempt
@role_required('admin')
def users(request):
    role = role_manage(request.user)

    # Check if the user is an admin
    if not check_login_admin(request.user):
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
        'user_role':role,
        'page_obj':page_obj,
        'start_number':start_number
    }
    return render(request, 'admin/users/users.html', context)

@role_required('admin')
def add_users(request):
    if not check_login_admin(request.user):
        return redirect('adminlogin')
    groups = Group.objects.all()
    role = role_manage(request.user)
    
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

            return JsonResponse({'success': True, 'message': 'User created successfully!'})
        except Exception as e:
            return JsonResponse({'success':False,'errors': {'server':str(e)}})
    context = {
    'user_role':role,
    'groups':groups
    }
    return render(request,'admin/users/add_user.html',context)

@csrf_exempt
@role_required('admin')
def delete_user(request, pk):
    if not check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'DELETE':
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

@role_required('admin')
def edit_user(request,pk):
    if not check_login_admin(request.user):
        return redirect('adminlogin')
    role = role_manage(request.user)
    
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
            for id in groupids:
                group = Group.objects.get(id=id)
                user.groups.add(group)

            return JsonResponse({'success': True,'message':'User Update Successfully!'})
        except Exception as e:
            return JsonResponse({'success':False,'errors':{'server':str(e)}})
    context = {
    'user_role':role,
    'groups':groups,
    'user':user_detail,
    'user_group_ids': user_group_ids
    }
    return render(request,'admin/users/edit_user.html',context)

#######################
# Category Management #
#######################

@role_required('inventory_manager')
def category(request):
    role = role_manage(request.user)
    search_query = request.GET.get('search','')
    category = Category.objects.filter(is_active=True,is_delete=False,category_name__icontains=search_query)
    paginator = Paginator(category,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
    'user_role':role,
    'category':category,
    'page_obj':page_obj
    }
    return render(request,'admin/category/category.html',context)

@role_required('inventory_manager')
def add_category(request):
    role = role_manage(request.user)
    context = {
    'user_role':role
    }
    if request.method == 'POST':

        category_name = request.POST.get('category_name')

        if not category_name:
            messages.error(request, 'Category name is required.')
            return render(request, 'admin/category/add_category.html', context)
        
        # Additional validation can go here (e.g., checking if the category already exists)
        if Category.objects.filter(category_name=category_name).exists():
            messages.error(request, 'Category already exists.')
            return render(request, 'admin/category/add_category.html', context)
        
        category = Category(
            category_name=category_name
        )
        try:
            category.save()
            messages.success(request, 'Category added successfully!')
            return render(request, 'admin/category/add_category.html',context)  
        except Exception as e:
            messages.error(request, f'Error saving category: {e}')
    
    return render(request, 'admin/category/add_category.html',context)

@role_required('inventory_manager')
def edit_category(request):
    role = role_manage(request.user)
    context = {
        'user_role': role
    }
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category_name = request.POST.get('category_name')
        category = get_object_or_404(Category, id=category_id)
        category.category_name = category_name
        category.save()
        messages.success(request, 'Category edited successfully')
        return JsonResponse({'success': True, 'message': 'Category edited successfully'})
    return render(request, 'admin/category/edit_category.html', context)

@csrf_exempt
@role_required('inventory_manager')
def delete_category(request,pk):
    if request.method == 'DELETE':
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

@role_required('inventory_manager')
def add_sub_category(request):
    role = role_manage(request.user)
    context = {
    'user_role':role
    }
    category = Category.objects.filter(parent_id=None)
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
    context = {
    'user_role':role,
    'category':category
    }
    return render(request, 'admin/category/add_sub_category.html',context)

######################
# Product Management #
######################

@role_required('inventory_manager')
def product(request):
    role = role_manage(request.user)
    products = Product.objects.filter(is_active=True, is_delete=False).select_related('category').prefetch_related('product__product', 'products__product_attribute')
    paginator = Paginator(products,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user_role':role,
        'page_obj':page_obj
    }

    return render(request,'admin/product/product.html',context)

@role_required('inventory_manager')
def add_products(request):
    role = role_manage(request.user)
    category = Category.objects.filter(parent_id=None)
    context = {
        'user_role':role,
        'category':category
    }
    if request.method == 'POST':
        name = request.POST.get('product_name')
        category_id = request.POST.get('category_id')
        images = request.FILES.getlist('product_images[]')
        print('images: ', images)
        if not name:
            messages.error(request,'Product Name is required')
            return render(request,'admin/product/add_product.html',context)
        if not category_id:
            messages.error(request,'Please Select Category')
            return render(request,'admin/product/add_product.html',context)
        
        try:
            product = Product.objects.create(name=name, category_id=category_id)
            for image in images:
                fs = FileSystemStorage(location='media/product_images')
                filename = fs.save(image.name, image)
                ProductImage.objects.create(product=product, image='product_images/' + filename)
            messages.success(request, 'Product Added Successfully')
        except IntegrityError:
            messages.error(request, 'Product with this name already exists in the selected category.')
        return render(request,'admin/product/add_product.html',context) 
    return render(request,'admin/product/add_product.html',context)

@role_required('inventory_manager')
def add_product_attribute(request):
    role = role_manage(request.user)
    context = {
        'user_role':role
    }
    if request.method == 'POST':
        attribute_name = request.POST.get('attribute_name')
        if not attribute_name:
            messages.error(request,'Enter attribute name')
            return render(request,'admin/product/add_product_attribute.html',context)
        if ProductAttribute.objects.filter(name=attribute_name).exists():
            messages.error(request, 'Product Attribute already exists.')
            return render(request,'admin/product/add_product_attribute.html',context)
        
        ProductAttribute.objects.create(name=attribute_name)
        messages.success(request,'Product Attribute Added Successfully')

        return render(request,'admin/product/add_product_attribute.html',context)
    return render(request,'admin/product/add_product_attribute.html',context)

@role_required('inventory_manager')
def add_product_attribute_value(request):
    product_attribute = ProductAttribute.objects.all()
    product = Product.objects.all()
    role = role_manage(request.user)
    context ={
        'user_role':role,
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

        ProductAttributeValue.objects.create(value=product_attribute_value,product_attribute_id=product_attribute_id,product_id=product_id)
        messages.success(request,'Product Attribute added successfully')
        return render(request,'admin/product/add_product_attribute_value.html',context)
    return render(request,'admin/product/add_product_attribute_value.html',context)