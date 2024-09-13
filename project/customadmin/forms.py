"""
Forms for the custom admin application.

This module contains forms for managing banners, email templates, orders, and flat pages.
"""

from django import forms
from django.contrib.flatpages.models import FlatPage

from .models import Banner, EmailTemplate

class BannerForm(forms.ModelForm):
    """
    Form for creating and editing banners.
    """
    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta options for BannerForm.
        """
        model = Banner
        fields = ['image', 'priority']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control'})
        }

    def clean(self):
        """
        Validate the image type and ensure priority uniqueness.
        """
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        priority = cleaned_data.get('priority')
        image_types = ['.png', '.jpeg', '.jpg']

        if image and not any(
            image.name.lower().endswith(ext) for ext in image_types
        ):
            raise forms.ValidationError(
                f"Unsupported file type: {image.name}. Please upload a PNG, JPEG, or JPG image."
            )

        if priority is not None:
            # Check if priority is already taken by another banner
            filters = {'priority': priority, 'is_active': True, 'is_delete': False}
            if self.instance.pk:
                # Exclude the current banner from the check
                if Banner.objects.exclude(pk=self.instance.pk).filter(**filters).exists(): # pylint: disable=E1101
                    raise forms.ValidationError(
                        f"Priority {priority} already exists. Please choose a different priority."
                    )
            else:
                # No current instance (creating a new banner)
                if Banner.objects.filter(**filters).exists(): # pylint: disable=E1101
                    raise forms.ValidationError(
                        f"Priority {priority} already exists. Please choose a different priority."
                    )

        return cleaned_data

class CustomFlatPageForm(forms.ModelForm):
    """
    Form for creating and editing flat pages.
    """
    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta options for FlatPageForm.
        """
        model = FlatPage
        fields = ['title', 'url', 'content', 'sites']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'sites': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }

    def clean_url(self):
        """
        Ensure the URL starts with a forward slash (/).
        """
        url = self.cleaned_data.get('url')
        if not url.startswith('/'):
            raise forms.ValidationError('URL must start with a forward slash (/).')
        return url

    def clean(self):
        """
        Ensure unique combination of title, URL, and sites.
        """
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        url = cleaned_data.get('url')
        sites = cleaned_data.get('sites')

        if title and url and sites:
            existing_flatpages = FlatPage.objects.filter(title=title, url=url, sites__in=sites) # pylint: disable=E1101
            if self.instance.pk:
                existing_flatpages = existing_flatpages.exclude(pk=self.instance.pk)

            if existing_flatpages.exists():
                raise forms.ValidationError(
                    'A FlatPage with this title and URL already exists for the selected sites.'
                )

        return cleaned_data

class EmailTemplateForm(forms.ModelForm):
    """
    Form for creating and editing email templates.
    """
    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta options for EmailTemplateForm.
        """
        model = EmailTemplate
        fields = ['subject', 'body', 'template_name', 'is_active']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'template_name': forms.TextInput(attrs={'class': 'form-control'})
        }
