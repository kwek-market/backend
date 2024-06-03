from django.contrib import admin
from .models import ExtendUser, SellerProfile
from django.apps import apps


class ExtendUserAdmin(admin.ModelAdmin):
    readonly_fields = ('id','pk', '__str__',)
# Register your models here.
admin.site.register(ExtendUser, ExtendUserAdmin)
admin.site.register(SellerProfile)

app = apps.get_app_config("graphql_auth")
for model_name, model in app.models.items():
    admin.site.register(model)
