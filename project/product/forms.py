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
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect(
                choices=[(i, str(i)) for i in range(1, 6)],  # Choices from 1 to 5
                attrs={'class': 'star-rating'}
            )
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
