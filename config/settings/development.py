from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'role_management',
        'USER':'root',
        'PASSWORD':'12345678',
        'HOST':'127.0.0.1',
        'PORT':'3306',
    }
}