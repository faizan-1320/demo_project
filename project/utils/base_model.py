# pylint: disable=R0903
"""Base Model for created_at and updated_at"""
from django.db import models

class BaseModel(models.Model):
    """BaseModel"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Meta class'''
        abstract = True
