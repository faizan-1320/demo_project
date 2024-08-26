from django.shortcuts import render,redirect,get_object_or_404
from .forms import LoginForm,UserForm,CustomUserCreationForm,AdressForm,ContactForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import Address,User
from project.customadmin.models import Banner
from project.product.models import Product,Category
from django.db.models import Min, Max

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

    min_price_filter = request.GET.get('min_price', None)
    max_price_filter = request.GET.get('max_price', None)

    min_price = Product.objects.aggregate(min_price=Min('price'))['min_price'] or 0
    max_price = Product.objects.aggregate(max_price=Max('price'))['max_price'] or 0

    if min_price_filter and max_price_filter:
        try:
            min_price_filter = float(min_price_filter)
            max_price_filter = float(max_price_filter)
        except ValueError:
            min_price_filter = min_price
            max_price_filter = max_price
    else:
        min_price_filter = min_price
        max_price_filter = max_price

    category_id = request.GET.get('category', None)
    
    if category_id:
        products = Product.objects.filter(category__id=category_id, is_active=True, is_delete=False, price__gte=min_price_filter, price__lte=max_price_filter).prefetch_related('product')
    else:
        products = Product.objects.filter(is_active=True, is_delete=False, price__gte=min_price_filter, price__lte=max_price_filter).prefetch_related('product')

    context = {
        'banners': banners,
        'products': products,
        'categories': category_tree,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'min_price_filter': min_price_filter,
        'max_price_filter': max_price_filter,
    }
    return render(request, 'front_end/index.html', context)


def auth_view(request):
    if request.method == 'POST':
        # Handle login form submission
        if 'login' in request.POST:
            login_form = LoginForm(request.POST)
            register_form = CustomUserCreationForm()
            
            if login_form.is_valid():
                email = login_form.cleaned_data['email']
                password = login_form.cleaned_data['password']
                user = authenticate(request, username=email, password=password)
                
                if user is not None:
                    login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, 'Email or Password does not exist')
        
        # Handle registration form submission
        elif 'register' in request.POST:
            register_form = CustomUserCreationForm(request.POST)
            login_form = LoginForm()
            
            if register_form.is_valid():
                try:
                    user = register_form.save(commit=False)
                    user.email = user.email.lower()
                    user.save()
                    login(request, user)
                    return redirect('home')
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
    cart=request.session.get('cart',{})

    logout(request)
    request.session['cart']=cart
    return redirect('home')

def forgot_password(request):
    return render(request,'front_end/authentication/forgot_password.html')

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
