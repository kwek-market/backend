from django.db import models

# Create your models here.


class AssetFile(models.Model):
    file = models.CharField(max_length=255)
    height = models.IntegerField(default=None)
    width = models.IntegerField(default=None)
    extension = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=255)
