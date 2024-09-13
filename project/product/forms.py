"""
Forms for the prduct application.

This module contains forms for managing product review,rating.
"""
from django import forms
from .models import Review, Rating,ProductAttribute

class ReviewForm(forms.ModelForm):
    """
    Form for Review.
    """
    class Meta: # pylint: disable=R0903
        """
        Meta options for ReviewForm.
        """
        model = Review
        fields = ['message']
        widgets = {
            'message':forms.Textarea(attrs={'class': 'form-control'})
        }

class RatingForm(forms.ModelForm):
    """
    Form for Rating.
    """
    class Meta: # pylint: disable=R0903
        """
        Meta options for RatingForm.
        """
        model = Rating
        fields = ['rating']
        widgets = {
            'rating':forms.TextInput(attrs={'class': 'form-control'})
        }

class ProductAttributeForm(forms.ModelForm):
    """
    Form for creating and editing product attributes.
    """
    class Meta: # pylint: disable=R0903
        """
        Meta options for ProductAttributeForm.
        """
        model = ProductAttribute
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }
