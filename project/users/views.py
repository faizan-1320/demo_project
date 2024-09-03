from django.shortcuts import render,redirect,get_object_or_404
from .forms import LoginForm,UserForm,CustomUserCreationForm,AdressForm,ContactForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import Address,User
from project.customadmin.models import Banner
from project.product.models import Product,Category
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings


def get_category_tree(categories, parent_id=None):
    """
    Recursively build a tree structure from a flat list of categories.
    """
    tree = []
    for category in categories.filter(parent_id=parent_id):
        children = get_category_tree(categories, parent_id=category.id)
        tree.append({
            'category': category,
            'children': children
        })
    return tree

# Create your views here.
def home(request):
    banners = Banner.objects.filter(is_active=True, is_delete=False)
    categories = Category.objects.filter(is_active=True, is_delete=False)
    category_tree = get_category_tree(categories)

    category_id = request.GET.get('category', None)
    
    if category_id:
        products = Product.objects.filter(category__id=category_id, is_active=True, is_delete=False).prefetch_related('product')
    else:
        products = Product.objects.filter(is_active=True, is_delete=False).prefetch_related('product')

    paginator = Paginator(products, 10)  # Show 10 products per page
    page = request.GET.get('page', 1)

    try:
        products_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_paginated = paginator.page(1)
    except EmptyPage:
        products_paginated = paginator.page(paginator.num_pages)

    context = {
        'banners': banners,
        'products': products_paginated,
        'categories': category_tree,
        'selected_category': category_id,
    }
    return render(request, 'front_end/index.html', context)

def auth_view(request):
    next_url = request.GET.get("next", settings.LOGIN_REDIRECT_URL)

    if request.method == 'POST':
        if 'login' in request.POST:
            login_form = LoginForm(request.POST)
            register_form = CustomUserCreationForm()
            
            if login_form.is_valid():
                email = login_form.cleaned_data['email']
                password = login_form.cleaned_data['password']
                user = authenticate(request, username=email, password=password)
                
                if user is not None:
                    login(request, user)
                    return redirect(next_url)
                else:
                    messages.error(request, 'Email or Password does not exist')
        
        elif 'register' in request.POST:
            register_form = CustomUserCreationForm(request.POST)
            login_form = LoginForm()
            
            if register_form.is_valid():
                try:
                    user = register_form.save(commit=False)
                    user.email = user.email.lower()
                    user.save()
                    messages.success(request,'Register Successfully')
                    return redirect('auth-view')
                except IntegrityError:
                    messages.error(request, 'A user with that email already exists.')
            else:
                for msg in register_form.error_messages:
                    messages.error(request, f'{msg}: {register_form.error_messages[msg]}')
    
    else:
        login_form = LoginForm()
        register_form = CustomUserCreationForm()
    
    context = {
        'login_form': login_form,
        'register_form': register_form
    }
    return render(request, 'front_end/authentication/auth_page.html', context)

def logoutUser(request):
    cart = request.session.get('cart', {})
    logout(request)
    request.session['cart'] = cart
    return redirect('home')

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Mail send successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request,'front_end/contact.html',{'form':form})

@login_required
def user_detail(request):
    user = request.user
    user_detail = User.objects.get(id=user.id)

    addresses = Address.objects.filter(user=user)

    return render(request, 'front_end/user/user_detail.html', {'user_detail': user_detail,'addresses': addresses})

@login_required
def user_detail_edit(request):
    user = request.user

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your details have been updated successfully.')
            return redirect('user')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserForm(instance=user)

    return render(request, 'front_end/user/user_detail_edit.html', {'form': form})

@login_required
def add_address(request):
    user = request.user
    if request.method == 'POST':
        address_form = AdressForm(request.POST)
        if address_form.is_valid():
            new_address = address_form.save(commit=False)
            new_address.user = user
            new_address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('user')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        address_form = AdressForm()
    return render(request,'front_end/user/add_address.html',{'address_form':address_form})

@login_required
def edit_address(request, pk):
    user = request.user
    address = get_object_or_404(Address, id=pk, user=user)
    
    if request.method == 'POST':
        address_form = AdressForm(request.POST, instance=address)
        if address_form.is_valid():
            address_form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('user')  # Redirect to the user profile or address list page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        address_form = AdressForm(instance=address)
    
    return render(request, 'front_end/user/edit_address.html', {'address_form': address_form})

@login_required
def delete_address(request, pk):
    user = request.user
    address = get_object_or_404(Address, id=pk, user=user)

    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
        return redirect('user')

    return render(request, 'front_end/user/confirm_delete_address.html', {'address': address})
