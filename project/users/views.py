from django.shortcuts import render,redirect
from .forms import LoginForm,UserForm,CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import Address

# Create your views here.
def home(request):
    return render(request,'front_end/index.html')

def view_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Email or Password does not exist')
    else:
        form = LoginForm()
    
    return render(request, 'front_end/authentication/login.html', {'form': form})

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.email = user.email.lower()
                user.save()
                login(request, user)
                return redirect('home')
            except IntegrityError:
                messages.error(request, 'A user with that email already exists.')
        else:
            for msg in form.error_messages:
                messages.error(request, f'{msg}: {form.error_messages[msg]}')
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form}
    return render(request, 'front_end/authentication/registration.html', context)

def forgot_password(request):
    return render(request,'front_end/authentication/forgot_password.html')

def contact_us(request):
    return render(request,'front_end/contact.html')

@login_required
def user_detail(request):
    user = request.user

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your details have been updated successfully.')
            return redirect('user-detail')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserForm(instance=user)

    addresses = Address.objects.filter(user=user)

    return render(request, 'front_end/user/user_detail.html', {'form': form,'addresses': addresses})