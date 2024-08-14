from django.db import models
from django.utils import timezone
from project.utils.base_model import BaseModel

# Create your models here.
class Banner(models.Model):
    image = models.ImageField(upload_to='banner')
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'

    def __str__(self):
        return self.image
    
from django.db import models

class ContactUs(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    is_replied = models.BooleanField(default=False)

    def __str__(self):
        return self.subject
    
class EmailTemplate(BaseModel):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    template_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.template_name