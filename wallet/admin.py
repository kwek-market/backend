from django.contrib import admin
from .models import WalletTransaction, Wallet
from django.apps import apps

# Register your models here.
admin.site.register(WalletTransaction) 
admin.site.register(Wallet) 