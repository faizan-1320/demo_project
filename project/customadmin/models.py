"""
This module contains models for the custom admin application, including
Banner, ContactUs, EmailTemplate, and NewsletterSubscriber models.
"""

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from project.utils.base_model import BaseModel # pylint: disable=E0401

class Banner(models.Model):
    """
    Model representing a banner for display.
    """
    image = models.ImageField(upload_to='banner')
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta options for BannerModel.
        """
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'

    def __str__(self):
        return str(self.image)

class ContactUs(BaseModel): # pylint: disable=too-few-public-methods
    """
    Model for managing contact us messages from users.
    """
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',  # Allows for phone numbers with country code
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    is_replied = models.BooleanField(default=False)

    def __str__(self):
        return str(self.subject)
class EmailTemplate(BaseModel): # pylint: disable=too-few-public-methods
    """
    Model for storing email templates used in the system.
    """
    subject = models.CharField(max_length=255)
    body = models.TextField()
    template_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.template_name)

class NewsletterSubscriber(BaseModel): # pylint: disable=too-few-public-methods
    """
    Model for managing newsletter subscribers.
    """
    email = models.EmailField(unique=True)
    is_subscribed = models.BooleanField(default=True)

    def __str__(self):
        return str(self.email)
