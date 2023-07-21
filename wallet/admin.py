from django.contrib import admin
from .models import *
from django.apps import apps

# Register your models here.
admin.site.register(WalletTransaction,
                    ) 
admin.site.register(
                    Wallet,
               
                    ) 
admin.site.register(
                    WalletRefund,
               
                    ) 
admin.site.register(
                    Invoice,
               
                    ) 
admin.site.register(
                    PurchasedItem,
              
                    ) 
admin.site.register(
                    StoreDetail
                    ) 