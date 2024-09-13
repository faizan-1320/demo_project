"""This custom user manager"""
from typing import Any # pylint: disable=W0611
from django.contrib.auth.models import UserManager

class CustomManager(UserManager):
    """This custom user manager"""
    def create_user(self, email, password, **extra_fields): # pylint: disable=W0221
        """This create user manager"""
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields): # pylint: disable=W0221
        """This create super user manager"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get('is_staff') is not True:
            return ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            return ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)
