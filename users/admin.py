from django.contrib import admin
from .models import ExtendUser,SellerProfile
from django.apps import apps
from .models import Category,Subcategory,Product,ProductImage,ProductOption,Keyword,ProductPromotion,Rating

# Register your models here.
admin.site.register(ExtendUser)
admin.site.register(SellerProfile)

app = apps.get_app_config("graphql_auth")
for model_name, model in app.models.items():
    admin.site.register(model)

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductOption)
admin.site.register(Keyword)
admin.site.register(ProductPromotion)
admin.site.register(Rating)