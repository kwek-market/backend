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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "django": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
    },
}
