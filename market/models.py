from django.db import models
from typing import Any
from django.contrib.postgres.fields import ArrayField
from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE
from users.models import ExtendUser as User
import uuid
from datetime import datetime

# Create your models here.


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, blank=False, null=True, unique=True)
    parent = models.ForeignKey("self", blank=True, null=True, related_name="child", on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

class Keyword(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    keyword = models.CharField(max_length=255, blank=False, null=True, unique=True)

    def __str__(self):
        return self.keyword


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product_title = models.CharField(max_length=255, blank=False, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, related_name="category", on_delete=models.CASCADE, null=True)
    subcategory = models.ForeignKey(Category, related_name="subcategory", on_delete=models.CASCADE, null=True, default=None)
    brand = models.CharField(max_length=255, blank=False, null=True)
    product_weight = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    charge_five_percent_vat = models.BooleanField(blank=False)
    return_policy = models.CharField(max_length=255, blank=True, null=True)
    warranty = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    keyword = ArrayField(models.CharField(max_length=250))
    clicks = models.IntegerField(default=0, blank=False)
    promoted = models.BooleanField(default=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    sales = models.PositiveBigIntegerField(default=0)


    def __str__(self):
        return self.product_title


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name='image', on_delete=models.CASCADE)
    image_url = models.TextField(blank=False, null=True)

    def __str__(self):
        return self.product


class ProductOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name="options", on_delete=models.CASCADE, null=True)
    size = models.CharField(max_length=255, blank=False, null=True)
    quantity = models.CharField(max_length=255, blank=False, null=True)
    price = models.FloatField(blank=False, null=True)
    discounted_price = models.FloatField(blank=False, null=True)
    option_total_price = models.FloatField(blank=False, null=True)

    def __str__(self):
        return self.product


class ProductPromotion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name="promo", on_delete=models.CASCADE, null=True)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name="product_rating", on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(blank=False, null=True)
    review = models.TextField(null=True)
    parent = models.ForeignKey("self", related_name="comment", on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    rated_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.full_name



class Newsletter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(max_length=255, unique=True)

    def __str__(self):
        return str(self.email)

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, related_name="user_carts", on_delete=models.CASCADE, null=True)
    ip = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    product = models.ForeignKey(Product, related_name="product_carts", on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.FloatField()
    cart = models.ForeignKey(Cart, related_name="cart_item", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.product_title} - {self.user_id.email}"


class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, related_name="user_wish", on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name="products_wished")
    created_at = models.DateTimeField(auto_now_add=True)

