"""
Django settings for kwek project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
load_dotenv()
SECRET_KEY = "yx6&m47urn&p8)1=p0d(!0edgy1$dx!pb%u5v5%i5r3*7h)qn-"

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = os.getenv("DEGUG", True)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "market",
    "kwek_auth",
    "asset_mgmt",
    "bill",
    "users",
    "notifications",
    "wallet",


    "graphene_django",
    "django_filters",
    "graphql_jwt.refresh_token.apps.RefreshTokenConfig",
    "graphql_auth",
    "corsheaders",
    "graphql_playground",
    
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kwek.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "kwek.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# if DEBUG:

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": config("DATABASE"),
#         "USER": config("USER_NAME"),
#         "PASSWORD": config("PASSWORD"),
#         "HOST": config("HOST"),
#         "PORT": config("PORT"),
#     }
# }
DATABASES = {
    "default": {
        # "ENGINE": "django.db.backends.postgresql",
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "d32s70iousao4l",
        "USER": "jvtkaahtroqcbg",
        "PASSWORD": "476b802ed25ea70a1be17da685811594d6aac0fb986b637e3c760c32c0a899fa",
        "HOST": "ec2-50-19-32-96.compute-1.amazonaws.com",
        "PORT": 5432,
    }
}
# import dj_database_url
# DATABASES = {"default":dj_database_url.parse('postgres://jvtkaahtroqcbg:476b802ed25ea70a1be17da685811594d6aac0fb986b637e3c760c32c0a899fa@ec2-50-19-32-96.compute-1.amazonaws.com:5432/d32s70iousao4l', conn_max_age=600)}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/asset/"
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
STATICFILES_DIRS = [BASE_DIR, "static"]
STATIC_ROOT = "/home/kwekxbyu/kwekapi.com/static/"
if DEBUG:
    MEDIA_ROOT = os.path.join(BASE_DIR, "asset")
else:
    MEDIA_ROOT = "/home/kwekxbyu/kwekapi.com/asset"


AUTH_USER_MODEL = "users.ExtendUser"

GRAPHENE = {
    "SCHEMA": "users.schema.schema",
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
    ],
}

AUTHENTICATION_BACKENDS = [
    # 'graphql_jwt.backends.JSONWebTokenBackend',
    "graphql_auth.backends.GraphQLAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

GRAPHQL_JWT = {
    "JWT_ALLOW_ANY_CLASSES": [
        "graphql_auth.mutations.Register",
    ],
    # "JWT_VERIFY_EXPIRATION": True,
    # "JWT_LONG_RUNNING_REFRESH_TOKEN" : True,
}

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REGISTER_MUTATION_FIELDS = {
    "email": "String",
    "username": "String",
    "full_name": "String",
}

BACKEND_DOMAIN = "http://www.kwekapi.com"
DOMAIN = "www.kwekmarket.com"
KWEK_EMAIL = "support@kwekmarket.com"
PHPWEB = "kwekmailapiphpmailsystem"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "gregoflash01@gmail.com"  # this is exactly the value 'apikey'
EMAIL_HOST_PASSWORD = "greg1998"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# ALLOWED_HOSTS = ['127.0.0.1', 'localhost','143.198.115.156', 'kwekapi.com', 'www.kwekapi.com']
# CORS_ORIGIN_ALLOW_ALL = False
ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = (
    "http://localhost:3000",
    "https://localhost:3000",
    "https://kwek.vercel.app",
    "http://kwek.vercel.app",
    "http://kwekapi.com",
    "https://kwekapi.com",
)

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
from corsheaders.defaults import default_methods

CORS_ALLOW_METHODS = list(default_methods) + [
    "POKE",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
FLUTTER_SEC_KEY = "FLWSECK-0d9c039a89fd946d83898a0a0b1e7b6c-X"

# import sys

# class Logger(object):
#     def __init__(self):
#         self.console = sys.stderr
#         self.file = open("runserver.log", "a")

#     def write(self, msg):
#         self.console.write(msg)
#         self.file.write(msg)

# sys.stderr = Logger()
# class OutLogger(object):
#     def __init__(self):
#         self.console = sys.stdout
#         self.file = open("runserver.log", "a")

#     def write(self, msg):
#         self.console.write(msg)
#         self.file.write(msg)

# sys.stdout = OutLogger()
