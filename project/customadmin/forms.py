from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class BannerForm(forms.Form):
    banner_images = MultipleFileField(
        label='Banner Image',
        required=True,
        widget=MultipleFileInput(attrs={'class': 'form-control'})
    )

    def clean_banner_images(self):
        images = self.files.getlist('banner_images')
        image_types = ['.png', '.jpeg', '.jpg']
        invalid_images = []

        for image in images:
            if not any(image.name.lower().endswith(ext) for ext in image_types):
                invalid_images.append(image.name)
        
        if invalid_images:
            raise forms.ValidationError(f"Unsupported file types: {', '.join(invalid_images)}. Please upload PNG, JPEG, or JPG images.")
        
        return images
    
class BannerEditForm(forms.Form):
    banner_image = forms.FileField(
        label='Banner Image',
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
    )

    def clean_banner_image(self):
        image = self.cleaned_data.get('banner_image')
        image_types = ['.png', '.jpeg', '.jpg']

        if image and not any(image.name.lower().endswith(ext) for ext in image_types):
            raise forms.ValidationError("Unsupported file type. Please upload PNG, JPEG, or JPG images.")
        
        return image