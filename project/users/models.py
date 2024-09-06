from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .managers import CustomManager
from project.utils import base_model
from project.product.models import Product
# Create your models here.
class User(AbstractBaseUser,PermissionsMixin):

    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True,unique=True)
    phone_number = models.CharField(max_length=15,null=True,blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_delete = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

class Address(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='address')
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Unset previous primary addresses for the user
            Address.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')

    def __str__(self):
        return f"{self.user.email} - {self.address[:20]}{' (Primary)' if self.is_primary else ''}"
    
class Wishlist(base_model.BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='wishlist')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='items')
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)