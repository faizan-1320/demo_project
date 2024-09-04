from django import forms
from .models import Banner,EmailTemplate
from django.contrib.flatpages.models import FlatPage
from project.order.models import Order
from django.core.exceptions import ValidationError
from project.product.models import ProductAttribute
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
        if priority is not None:
            if self.instance.pk:
                existing_banners = Banner.objects.filter(priority=priority,is_active=True,is_delete=False).exclude(pk=self.instance.pk)
            else:
                existing_banners = Banner.objects.filter(priority=priority,is_active=True,is_delete=False)

            if existing_banners.exists():
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
    def clean_url(self):
        url = self.cleaned_data.get('url')
        if not url.startswith('/'):
            raise forms.ValidationError('URL must start with a forward slash (/).')
        return url

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        url = cleaned_data.get('url')
        sites = cleaned_data.get('sites')

        if title and url and sites:
            # Check if a FlatPage with the same title and URL exists for the given sites
            existing_flatpages = FlatPage.objects.filter(title=title, url=url, sites__in=sites)
            if self.instance.pk:
                existing_flatpages = existing_flatpages.exclude(pk=self.instance.pk)

            if existing_flatpages.exists():
                raise forms.ValidationError('A FlatPage with this title and URL already exists for the selected sites.')

        return cleaned_data
    
class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model=EmailTemplate
        fields = ['subject','body','template_name','is_active']
        widgets = {
            'subject':forms.TextInput(attrs={'class':'form-control'}),
            'body':forms.Textarea(attrs={'class':'form-control','row':10}),
            'template_name':forms.TextInput(attrs={'class':'form-control'})
        }
    
class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(choices=Order.status_choice,attrs={'class':'form-control'})
        }
    
    def clean_status(self):
        new_status = self.cleaned_data['status']
        current_status = self.instance.status

        if new_status < current_status:
            raise ValidationError('You can not move the status to an earlier stage.')
        
        return new_status

class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ['name']
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'})
        }
