from django.db import models
import django
from datetime import datetime, timedelta
from django.contrib.postgres.fields import ArrayField
from users.models import ExtendUser as User
import uuid

# Create your models here.


class Category(models.Model):
    class Visibility(models.TextChoices):
        PUBLISHED = "published", "Published"
        SCHEDULED = "scheduled", "Scheduled"
        HIDDEN = 'hidden', "Hidden"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, blank=False, null=True, unique=True)
    icon = models.URLField(blank=True, null=True)
    visibility = models.CharField(max_length=255, choices=Visibility.choices, default=Visibility.PUBLISHED)
    publish_date = models.DateField(null=True, blank=True)
    parent = models.ForeignKey("self", blank=True, null=True, related_name="child", on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = "categories"
        

    def __str__(self):
        return self.name + " " + self.visibility

class Keyword(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    keyword = models.CharField(max_length=255, blank=False, null=True, unique=True)

    def __str__(self):
        return self.keyword

class Sales(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="sales")
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    

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
    clicks = models.IntegerField(default=0)
    promoted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)


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
    product = models.ForeignKey(Product, related_name="promo", on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=django.utils.timezone.now)
    end_date = models.DateTimeField(default=django.utils.timezone.now)
    days = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    amount = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    reach = models.IntegerField(default=0)
    link_clicks = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_title

    def save(self, *args, **kwargs):
        from datetime import timedelta
        d = timedelta(days=self.days)
        self.end_date = self.start_date + d

        super().save(*args, **kwargs)

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
class ContactMessage(models.Model):
    email = models.EmailField(max_length=255)
    name = models.CharField(max_length=255)
    message = models.TextField(max_length=255, null=False)
    sent_at = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return str(self.email)

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, related_name="user_carts", on_delete=models.CASCADE, null=True)
    ip = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name="product_carts", on_delete=models.CASCADE)
    product_option_id = models.CharField(max_length=225, default="lucky_cart")
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.FloatField(blank=False)
    cart = models.ForeignKey(Cart, related_name="cart_item", on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.product_title} - {self.product.user}"


class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="user_wish", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class WishListItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name="products_wished", on_delete=models.CASCADE)
    wishlist = models.ForeignKey(Wishlist, related_name="wishlist_item", on_delete=models.CASCADE)

class FlashSales(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(ProductOption, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    number_of_days = models.IntegerField(default=1)
    discount_percent = models.IntegerField(default=1)
    status = models.BooleanField(default=False)

