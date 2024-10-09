"""
Forms for the custom admin application.

This module contains forms for managing orders.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Order

class OrderStatusForm(forms.ModelForm):
    """
    Form for updating the status of an order.
    """

    class Meta:  # pylint: disable=R0903
        """
        Meta options for OrderStatusForm.
        """
        model = Order
        fields = ['status', 'payment_status']
        widgets = {
            'status': forms.Select(choices=Order.status_choice, attrs={'class': 'form-control'}),
            'payment_status': forms.Select(choices=Order.payment_status_choice, attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hide payment_status field if payment method is PayPal
        if self.instance.payment_method == 'paypal':
            self.fields['payment_status'].widget = forms.HiddenInput()  # Hide payment status field

    def clean_status(self):
        """
        Ensure that the status is not moved to an earlier stage.
        """
        new_status = self.cleaned_data['status']
        current_status = self.instance.status

        if new_status < current_status:
            raise ValidationError('You cannot move the status to an earlier stage.')

        return new_status

