# pylint: disable=E0401,R1705,C0206,E1101,R0914,E1120
"""
Views for the product application.

This module contains views for listing, creating, editing, and deleting User.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from project.customadmin.models import Banner
from project.product.models import Product, Category
from .models import Address, User, Wishlist
from .forms import (LoginForm, UserForm,
    CustomUserCreationForm, AdressForm, ContactForm, NewsletterForm)

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

def home(request):
    """
    View for the homepage. Displays banners, categories, and products.
    Handles filtering products based on selected category and pagination.
    """
    # Fetch active banners and categories
    banners = Banner.objects.filter(is_active=True, is_delete=False)
    categories = Category.objects.filter(is_active=True, is_delete=False)
    category_tree = get_category_tree(categories)

    # Get selected category from query parameters
    category_id = request.GET.get('category', None)

    # Filter products based on the selected category
    if category_id:
        selected_category = get_object_or_404(
        Category, id=category_id, is_active=True, is_delete=False)
        subcategories = Category.objects.filter(
        parent=selected_category, is_active=True, is_delete=False)
        categories_to_filter = [selected_category] + list(subcategories)
        products = Product.objects.filter(
        category__in=categories_to_filter, is_active=True, is_delete=False)
    else:
        # Display all active products if no category is selected
        products = Product.objects.filter(
        is_active=True, is_delete=False).prefetch_related('product')

    # Fetch featured products
    featured_products = Product.objects.filter(is_features=True, is_active=True, is_delete=False)

    # Paginate products
    paginator = Paginator(products, 12)
    featured_paginator = Paginator(featured_products, 12)

    page = request.GET.get('page', 1)

    try:
        products_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_paginated = paginator.page(1)
    except EmptyPage:
        products_paginated = paginator.page(paginator.num_pages)

    # Paginate featured products separately
    try:
        featured_products_paginated = featured_paginator.page(page)
    except PageNotAnInteger:
        featured_products_paginated = featured_paginator.page(1)
    except EmptyPage:
        featured_products_paginated = featured_paginator.page(featured_paginator.num_pages)

    # Handle newsletter subscription form submission
    form = NewsletterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('home')

    # Prepare context for rendering the template
    context = {
        'banners': banners,
        'products': products_paginated,
        'featured_products': featured_products_paginated,
        'categories': category_tree,
        'selected_category': category_id,
        'form': form,
    }

    return render(request, 'front_end/index.html', context)

def auth_view(request):
    """
    View for user authentication: login and registration.
    Handles form submissions for both login and registration.
    """
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
                    messages.success(request, 'Login Successfully')
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
                    messages.success(request, 'Register Successfully')
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

def logout_user(request):
    """
    Log out the current user and preserve the cart session.
    """
    cart = request.session.get('cart', {})
    logout(request)
    request.session['cart'] = cart
    return redirect('home')

def contact_us(request):
    """
    View for the 'Contact Us' page. Handles form submission for contacting the site admin.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mail sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'front_end/contact.html', {'form': form})

@login_required
def user_detail(request):
    """
    View to display the logged-in user's details and addresses.
    """
    user = request.user
    user_detail_data = User.objects.get(id=user.id)
    addresses = Address.objects.filter(user=user)

    return render(request,
            'front_end/user/user_detail.html', 
    {'user_detail': user_detail_data, 'addresses': addresses})

@login_required
def user_detail_edit(request):
    """
    View for editing the logged-in user's details.
    """
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
    """
    View for adding a new address for the logged-in user.
    """
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
    return render(request, 'front_end/user/add_address.html', {'address_form': address_form})

@login_required
def edit_address(request, pk):
    """
    View for editing an existing address of the logged-in user.
    """
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
    """
    View for deleting an address of the logged-in user.
    """
    user = request.user
    address = get_object_or_404(Address, id=pk, user=user)

    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
        return redirect('user')

    return render(request, 'front_end/user/confirm_delete_address.html', {'address': address})

@login_required
def add_to_wishlist(request, product_id):
    """
    Add a product to the logged-in user's wishlist.
    """
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        if wishlist_item.is_delete:
            wishlist_item.is_delete = False
            wishlist_item.is_active = True
            wishlist_item.save()
            messages.success(request, 'Product added to your wishlist.')
            return redirect('home')

        else:
            messages.error(request, 'This product is already in your wishlist.')
            return redirect('home')

    else:
        messages.success(request, 'Product added to your wishlist.')
    return redirect('home')

@login_required
def remove_from_wishlist(request, product_id):
    """
    Remove a product from the logged-in user's wishlist.
    """
    if request.method == 'POST':
        wishlist_item = get_object_or_404(
        Wishlist, user=request.user,
        product_id=product_id, is_active=True, is_delete=False)
        wishlist_item.is_active = False
        wishlist_item.is_delete = True
        wishlist_item.save()
        messages.success(request, 'Product removed from wishlist')
        return redirect('wishlist')

    messages.error(request, 'Invalid request')
    return redirect('wishlist')

@login_required
def wish_list(request):
    """
    View to display the logged-in user's wishlist.
    """
    wishlist = Wishlist.objects.filter(user=request.user, is_active=True, is_delete=False)
    context = {
        'wishlist': wishlist
    }
    return render(request, 'front_end/wishlist/wishlist.html', context)
