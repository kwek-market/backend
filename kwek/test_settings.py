# test_settings.py

from .settings import *
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_database",  
        "USER": "test_user",  
        "PASSWORD": "test_password",  
        "HOST": "localhost",
        "PORT": "5432",
    }
}
