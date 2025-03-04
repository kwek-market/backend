from ast import Or
from django.contrib import admin

# Register your models here.

from .models import Order, Payment, Billing, Pickup, Coupon, OrderProgress

class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('id','pk', '__str__',)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Billing)
admin.site.register(Pickup)
admin.site.register(Coupon)
admin.site.register(OrderProgress)
