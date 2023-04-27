from django.contrib import admin
from .models import WalletTransaction
from django.apps import apps

# Register your models here.
admin.site.register(WalletTransaction) 