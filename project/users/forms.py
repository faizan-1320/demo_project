from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import User,Address
from project.customadmin.models import ContactUs,NewsletterSubscriber
from django.contrib import messages
class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email",)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email",)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name','phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class AdressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields =['address','city','country','district','postcode','is_primary']
        widgets = {
            'address':forms.Textarea(attrs={'class':'form-control'}),
            'city':forms.TextInput(attrs={'class':'form-control'}),
            'country':forms.TextInput(attrs={'class':'form-control'}),
            'district':forms.TextInput(attrs={'class':'form-control'}),
            'postcode':forms.TextInput(attrs={'class':'form-control'})
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['name','subject','email','message']
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'subject':forms.TextInput(attrs={'class':'form-control'}),
            'email':forms.EmailInput(attrs={'class':'form-control'}),
            'message':forms.Textarea(attrs={'class':'form-control'}),
        }

class NewsletterForm(forms.ModelForm):
    class Meta:
        model =NewsletterSubscriber
        fields = ['email']
        widgets ={'email':forms.EmailInput(attrs={'class':'form-control'})}

    def save(self, request, commit=True):
        email = self.cleaned_data['email']
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)

        if created:
            messages.success(request, 'You have successfully subscribed to our newsletter!')
        else:
            messages.info(request, 'You are already subscribed.')

        return subscriber
