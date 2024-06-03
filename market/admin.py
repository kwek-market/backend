from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductImage,
    ProductOption,
    Keyword,
    ProductPromotion,
    Rating,
    Cart,
    CartItem,
    FlashSales,
    ProductCharge,
    StateDeliveryFee

)
from django.apps import apps


admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductOption)
admin.site.register(Keyword)
admin.site.register(ProductPromotion)
admin.site.register(Rating)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(FlashSales)
admin.site.register(StateDeliveryFee)
admin.site.register(ProductCharge)
# Register your models here.

class CustomCategoryAdmin(admin.ModelAdmin):
    search_fields = ("visibility__exact", )
    list_filter = ("visibility", )
admin.site.register(Category, CustomCategoryAdmin)    
    
