from django import forms
from .models import Coupon
from datetime import date

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code','discount_amount','discount_percentage','start_date','end_date']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        discount_amount = cleaned_data.get('discount_amount')
        discount_percentage = cleaned_data.get('discount_percentage')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if discount_amount > 0 and discount_percentage > 0:
            raise forms.ValidationError('You can only set either a fixed discount amount or a percentage discount, not both.')
        
        if start_date and start_date < date.today():
            raise forms.ValidationError('Start date cannot be in the past.')
        if end_date and end_date<start_date:
            raise forms.ValidationError('End date must be after the start date.')
        return cleaned_data