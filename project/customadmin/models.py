from django.db import models
from django.utils import timezone

# Create your models here.
class Banner(models.Model):
    image = models.ImageField(upload_to='banner')
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'