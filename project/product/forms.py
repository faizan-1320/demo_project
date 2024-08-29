from django import forms
from .models import Review, Rating

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['message']
        widgets = {
            'message':forms.Textarea(attrs={'class': 'form-control'})
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating':forms.TextInput(attrs={'class': 'form-control'})
        }
