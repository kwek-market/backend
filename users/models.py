from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class ExtendUser(AbstractUser):
    email = models.EmailField(blank=False, max_length=255, verbose_name="email", unique=True)
    full_name = models.CharField(blank=False, max_length=255, verbose_name="full_name")

    USERNAME_FIELD = "username"
    EmailField = "email"


