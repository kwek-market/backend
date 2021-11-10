from django.db import models
from typing import Any
from django.contrib.postgres.fields import ArrayField
from django.apps import apps as django_apps
from django.contrib.auth import get_user_model

# Create your models here.

SUBCATEGORY_MODEL = "market.Subcategory"


class VerboseSubCategoryManager(models.Manager):
    def get_queryset(self):
        q_set = super().get_queryset()
        subcategory_cls = django_apps.get_model(SUBCATEGORY_MODEL, require_ready=False)
        for i in q_set:
            i.child = subcategory_cls.objects.filter(pk__in=i.child)
            i.parent = subcategory_cls.objects.filter(pk__in=i.parent)

        return q_set

    def get(self, *args: Any, **kwargs: Any):
        subcategory = super().get(*args, **kwargs)
        subcategory_cls = django_apps.get_model(SUBCATEGORY_MODEL, require_ready=False)
        subcategory.child = subcategory_cls.objects.filter(pk__in=subcategory.child)
        subcategory.parent = subcategory_cls.objects.filter(pk__in=subcategory.parent)
        return subcategory


class Category(models.Model):
    name = models.CharField(max_length=255, blank=False, null=True, unique=True)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=255, blank=False, null=True, unique=True)
    categories = models.ManyToManyField("Category", related_name="subcategories")
    parent = ArrayField(models.IntegerField(), blank=True, default=list)
    child = ArrayField(models.IntegerField(), blank=True, default=list)

    objects = models.Manager()
    verbose_sub_category = VerboseSubCategoryManager()

    def __str__(self):
        return self.name


class Keyword(models.Model):
    keyword = models.CharField(max_length=255, blank=False, null=True, unique=True)

    def __str__(self):
        return self.keyword


class Product(models.Model):
    product_title = models.CharField(max_length=255, blank=False, null=True)
    user = models.ForeignKey("users.ExtendUser", on_delete=models.CASCADE, null=True)
    subcategory = models.ForeignKey(
        "market.Subcategory", on_delete=models.CASCADE, null=True
    )
    brand = models.CharField(max_length=255, blank=False, null=True)
    product_weight = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    charge_five_percent_vat = models.BooleanField(blank=False)
    return_policy = models.CharField(max_length=255, blank=True, null=True)
    warranty = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    keyword = models.ManyToManyField("market.Keyword", related_name="keywords")
    clicks = models.IntegerField(default=0, blank=False)
    promoted = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return self.product_title


class ProductImage(models.Model):
    product = models.ForeignKey("market.Product", on_delete=models.CASCADE, null=True)
    image_url = models.TextField(blank=False, null=True)

    def __str__(self):
        return self.product


class ProductOption(models.Model):
    product = models.ForeignKey(
        "market.Product", related_name="options", on_delete=models.CASCADE, null=True
    )
    size = models.CharField(max_length=255, blank=False, null=True)
    quantity = models.CharField(max_length=255, blank=False, null=True)
    price = models.FloatField(blank=False, null=True)
    discounted_price = models.FloatField(blank=False, null=True)
    option_total_price = models.FloatField(blank=False, null=True)

    def __str__(self):
        return self.product


class ProductPromotion(models.Model):
    product = models.ForeignKey("market.Product", on_delete=models.CASCADE, null=True)
    start_date = models.CharField(max_length=255, blank=False, null=True)
    end_date = models.CharField(max_length=255, blank=False, null=True)
    days = models.IntegerField(blank=False, null=True)
    active = models.BooleanField(default=True, blank=False, null=True)
    amount = models.FloatField(blank=False, null=True)
    reach = models.IntegerField(default=0, blank=False, null=True)
    link_clicks = models.IntegerField(default=0, blank=False, null=True)

    def __str__(self):
        return self.keyword


class Rating(models.Model):
    product = models.ForeignKey("market.Product", on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(blank=False, null=True)
    comment = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    email = models.EmailField(blank=False, null=True)
    rated_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product

class Newsletter(models.Model):
    email = models.EmailField(max_length=255, unique=True)

    def __str__(self):
        return str(self.email)