from django.shortcuts import render,redirect
from .models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .forms import CustomUserCreationForm
from django.db import IntegrityError

# Create your views here.
def home(request):
    return render(request,'front_end/index.html')


def view_login(request):
    page = 'login'
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request,'User does not exist')

        user = authenticate(request,email=email,password=password)


        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username or Password does not exist')
    context = {'page':page}
    return render(request,'front_end/authentication/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                print(user)
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