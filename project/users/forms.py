"""
Forms for the user application.

This module contains forms for managing user create,
user change,login,contact,address,newsletter.
"""
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib import messages
from project.customadmin.models import ContactUs,NewsletterSubscriber # pylint: disable=E0401
from .models import User,Address
class CustomUserCreationForm(UserCreationForm):
    """
    Form for RegisterForm.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-control'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'form-control'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'form-control'})
    )
    
    class Meta:
        """
        Meta Class.
        """
        model = User
        fields = ("email", "password1", "password2")


class CustomUserChangeForm(UserChangeForm):
    """
    Form for CustomUserChangeForm.
    """
    class Meta: # pylint: disable=R0903
        """
        Meta Class.
        """
        model = User
        fields = ("email",)

class UserForm(forms.ModelForm):
    """
    Form for UserForm.
    """
    class Meta: # pylint: disable=R0903
        """
        Meta Class.
        """
        model = User
        fields = ['first_name', 'last_name','phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LoginForm(forms.Form):
    """
    Form for LoginForm.
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Enter your email','class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter your password','class': 'form-control'}))

class AdressForm(forms.ModelForm):
    """
    Form for AdressForm.
    """
    class Meta: # pylint: disable=R0903
        """
        Meta Class.
        """
        model = Address
        fields =['address','address_type','city','country','district','postcode','is_primary']
        widgets = {
            'address':forms.Textarea(attrs={'class':'form-control'}),
            'address_type':forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'city':forms.TextInput(attrs={'class':'form-control'}),
            'country':forms.TextInput(attrs={'class':'form-control'}),
            'district':forms.TextInput(attrs={'class':'form-control'}),
            'postcode':forms.TextInput(attrs={'class':'form-control'}),
        }

class ContactForm(forms.ModelForm):
    """
    Form for ContactForm.
    """
    class Meta: # pylint: disable=R0903
        """
        Meta Class.
        """
        model = ContactUs
        fields = ['name','subject','email','message']
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'subject':forms.TextInput(attrs={'class':'form-control'}),
            'email':forms.EmailInput(attrs={'class':'form-control'}),
            'message':forms.Textarea(attrs={'class':'form-control'}),
        }

class NewsletterForm(forms.ModelForm):
    """
    Form for NewsletterForm.
    """
    class Meta: # pylint: disable=R0903
        """
        Meta Class.
        """
        model =NewsletterSubscriber
        fields = ['email']
        widgets ={'email':forms.EmailInput(attrs={'class':'form-control'})}

    def save(self, request, commit=True): # pylint: disable=W0237
        """
        Function to save.
        """
        email = self.cleaned_data['email']
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)

        if created:
            messages.success(request, 'You have successfully subscribed to our newsletter!')
        else:
            messages.info(request, 'You are already subscribed.')

        return subscriber
