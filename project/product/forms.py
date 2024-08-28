from django import forms
from .models import Review, Rating

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'name', 'email', 'message']
        widgets = {
            'title':forms.TextInput(attrs={'class': 'form-control'}),
            'name':forms.TextInput(attrs={'class': 'form-control'}),
            'email':forms.EmailInput(attrs={'class': 'form-control'}),
            'message':forms.Textarea(attrs={'class': 'form-control'})
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating':forms.TextInput(attrs={'class': 'form-control'})
        }
