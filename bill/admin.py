from ast import Or
from django.contrib import admin

# Register your models here.

from .models import Order, Payment, Billing, Pickup

admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Billing)
admin.site.register(Pickup)
