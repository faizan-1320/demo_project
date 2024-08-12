from django import forms
from .models import Banner
from django.contrib.flatpages.models import FlatPage
class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['image','priority']
        widgets = {
            'image':forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'priority':forms.NumberInput(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        priority = cleaned_data.get('priority')
        image_types = ['.png', '.jpeg', '.jpg']
        if image and not any(image.name.lower().endswith(ext) for ext in image_types):
            raise forms.ValidationError(f"Unsupported file type: {image.name}. Please upload a PNG, JPEG, or JPG image.")
        
        # Validate unique priority
        if Banner.objects.filter(priority=priority).exists():
            raise forms.ValidationError(f"Priority {priority} already exists. Please choose a different priority.")
        
        return cleaned_data
    
class CustomFlatPageForm(forms.ModelForm):
    class Meta:
        model = FlatPage
        fields = ['title', 'url', 'content','sites']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'sites': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }