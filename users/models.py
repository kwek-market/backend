from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class ExtendUser(AbstractUser):
    email = models.EmailField(blank=False, max_length=255, verbose_name="email", unique=True)
    full_name = models.CharField(blank=False, max_length=255, verbose_name="full_name")
    phone_number = models.CharField(blank=True, max_length=255, verbose_name="full_name")
    is_verified = models.BooleanField(default=False, verbose_name="is_verified")
    is_seller = models.BooleanField(default=False, verbose_name="is_seller")


    USERNAME_FIELD = "username"
    EmailField = "email"

class SellerProfile(models.Model):
    user = models.ForeignKey(ExtendUser, on_delete=models.CASCADE, null=True)
    firstname = models.CharField(max_length=255, blank=False, null=True)
    lastname = models.CharField(max_length=255, blank=False, null=True)
    phone_number = models.CharField(max_length=255, blank=False, null=True)
    shop_name = models.CharField(max_length=255, blank=False, null=True)
    shop_url = models.CharField(max_length=255, blank=False, null=True)
    shop_address = models.CharField(max_length=255, blank=False, null=True)
    state = models.CharField(max_length=255, blank=False, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    lga = models.CharField(max_length=255, blank=False, null=True)
    landmark = models.CharField(max_length=255, blank=False, null=True)
    how_you_heard_about_us = models.CharField(max_length=255, blank=False, null=True)
    accepted_policy = models.BooleanField(blank=False)
    store_banner_url = models.CharField(max_length=255, blank=True, null=True)
    store_description = models.CharField(max_length=255, blank=True, null=True)
    prefered_id = models.CharField(max_length=255, blank=True, null=True)
    prefered_id_url = models.CharField(max_length=255, blank=True, null=True)
    bvn = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_sort_code = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=255, blank=True, null=True)
    bank_account_name = models.CharField(max_length=255, blank=True, null=True)
    seller_is_verified = models.BooleanField(default=False, verbose_name="seller_is_verified")
    bank_account_is_verified = models.BooleanField(default=False, verbose_name="bank_account_is_verified")
    accepted_vendor_policy = models.BooleanField(default=False, verbose_name="accepted_vendor_policy")
    

    def __str__(self):
        return self.user

class Category(models.Model):
    sub_category = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=False, null=True)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=255, blank=False, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    parentcategory = models.CharField(max_length=255, blank=True, null=True)
    childcategory = models.CharField(max_length=255, blank=True, null=True)
    parent = models.BooleanField(blank=False)
    child = models.BooleanField(blank=False)

    def __str__(self):
        return self.name

class Keyword(models.Model):
    keyword = models.CharField(max_length=255, blank=False, null=True)

    def __str__(self):
        return self.keyword


class Product(models.Model):
    product_title = models.CharField(max_length=255, blank=False, null=True)
    user = models.ForeignKey(ExtendUser, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True)
    brand = models.CharField(max_length=255, blank=False, null=True)
    product_weight = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.TextField(blank=True,null=True)
    charge_five_percent_vat = models.BooleanField(blank=False)
    return_policy = models.CharField(max_length=255, blank=True, null=True)
    warranty = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    keyword = models.ManyToManyField(Keyword, related_name="keywords")
    clicks  = models.IntegerField(default=0, blank=False)
    promoted  = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return self.product_title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    image_url = models.TextField(blank=False, null=True)

    def __str__(self):
        return self.product


class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    size = models.CharField(max_length=255, blank=False, null=True)
    quantity = models.CharField(max_length=255, blank=False, null=True)
    price = models.FloatField(blank=False, null=True)
    discounted_price = models.FloatField(blank=False, null=True)
    option_total_price = models.FloatField(blank=False, null=True)

    def __str__(self):
        return self.product


class ProductPromotion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    start_date = models.CharField(max_length=255, blank=False, null=True)
    end_date = models.CharField(max_length=255, blank=False, null=True)
    days  = models.IntegerField(blank=False, null=True)
    active  = models.BooleanField(default=True,blank=False, null=True)
    amount = models.FloatField(blank=False, null=True)
    reach = models.IntegerField(default=0,blank=False, null=True)
    link_clicks = models.IntegerField(default=0,blank=False, null=True)

    def __str__(self):
        return self.keyword

class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(blank=False, null=True)
    comment = models.TextField(blank=True,null=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    email = models.EmailField(blank=False, null=True)
    rated_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product
