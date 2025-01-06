# test_settings.py

from .settings import *
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("TEST_DATABASE", "test_database"),  
        "USER": os.getenv("TEST_USER", "test_user"),  
        "PASSWORD": os.getenv("TEST_PASSWORD", "test_password"),  
        "HOST": os.getenv("TEST_HOST", "localhost"),
        "PORT": os.getenv("TEST_PORT", "5432"),
    }
}
