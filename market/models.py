import uuid
from datetime import datetime, timedelta

import django
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone

from bill.models import Order
from users.models import ExtendUser as User

# Create your models here.


class Category(models.Model):
    class Visibility(models.TextChoices):
        PUBLISHED = "published", "Published"
        SCHEDULED = "scheduled", "Scheduled"
        HIDDEN = "hidden", "Hidden"

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(
        max_length=255, blank=False, null=True, unique=True, db_index=True
    )
    icon = models.URLField(blank=True, null=True)
    visibility = models.CharField(
        max_length=255, choices=Visibility.choices, default=Visibility.PUBLISHED
    )
    publish_date = models.DateField(null=True, blank=True)
    parent = models.ForeignKey(
        "self", blank=True, null=True, related_name="child", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "categories"
        indexes = [
            models.Index(fields=["visibility"], name="visibility_idx"),
        ]

    def __str__(self):
        return self.name + " " + self.visibility


class Keyword(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    keyword = models.CharField(
        max_length=255, blank=False, null=True, unique=True, db_index=True
    )

    def __str__(self):
        return self.keyword


class Sales(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="sales"
    )
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)


class ProductQuerySet(models.QuerySet):
    def with_available_options(self):
        return self.annotate(
            available_options=Count("options", filter=Q(options__quantity__gt=0))
        ).filter(available_options__gt=0)

    def available(self):
        return self.with_available_options()


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def available(self):
        return self.get_queryset().with_available_options()


class Product(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    product_title = models.CharField(
        max_length=255, blank=False, null=True, db_index=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(
        Category, related_name="category", on_delete=models.CASCADE, null=True
    )
    subcategory = models.ForeignKey(
        Category,
        related_name="subcategory",
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )
    brand = models.CharField(max_length=255, blank=False, null=True, db_index=True)
    product_weight = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    charge_five_percent_vat = models.BooleanField(blank=False)
    return_policy = models.CharField(max_length=255, blank=True, null=True)
    warranty = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    keyword = ArrayField(models.CharField(max_length=250), db_index=True)
    clicks = models.IntegerField(default=0)
    promoted = models.BooleanField(default=False, db_index=True)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    def __str__(self):
        return self.product_title


class ProductImage(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    product = models.ForeignKey(Product, related_name="image", on_delete=models.CASCADE)
    image_url = models.TextField(blank=False, null=True)

    def __str__(self):
        return self.product.product_title


class ProductOption(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    product = models.ForeignKey(
        Product, related_name="options", on_delete=models.CASCADE, null=True
    )
    size = models.CharField(max_length=255, blank=False, null=True, db_index=True)
    color = models.CharField(max_length=255, blank=False, null=True, db_index=True)
    quantity = models.CharField(max_length=255, blank=False, null=True)
    price = models.FloatField(blank=False, null=True)
    discounted_price = models.FloatField(blank=False, null=True)
    option_total_price = models.FloatField(blank=False, null=True)

    def __str__(self):
        return f"{self.id}"


def get_product_charge(self) -> float:
    charge = ProductCharge.objects.first()
    if not charge:
        charge = ProductCharge.objects.create(has_fixed_amount=True, charge=0.00)

    charge_amount = (
        charge.charge if charge.has_fixed_amount else self.price * (charge.charge / 100)
    )
    return charge_amount


def get_product_price(self):
    charge_amount = self.get_product_charge()
    return self.price + charge_amount


def get_product_discounted_price(self):
    if self.discounted_price <= 0:
        return self.discounted_price
    charge_amount = self.get_product_charge()
    return self.discounted_price + charge_amount


class ProductPromotion(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    product = models.ForeignKey(Product, related_name="promo", on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=django.utils.timezone.now, db_index=True)
    end_date = models.DateTimeField(default=django.utils.timezone.now, db_index=True)
    days = models.IntegerField(default=1)
    active = models.BooleanField(default=True, db_index=True)
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
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    product = models.ForeignKey(
        Product, related_name="product_rating", on_delete=models.CASCADE, null=True
    )
    rating = models.IntegerField(blank=False, null=True, db_index=True)
    review = models.TextField(null=True)
    parent = models.ForeignKey(
        "self", related_name="comment", on_delete=models.CASCADE, null=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    rated_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.full_name


class Newsletter(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    email = models.EmailField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return str(self.email)


class ContactMessage(models.Model):
    email = models.EmailField(max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    message = models.TextField(max_length=255, null=False)
    sent_at = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return str(self.email)


class Cart(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    user = models.OneToOneField(
        User, related_name="user_carts", on_delete=models.CASCADE, null=True
    )
    ip = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItemQuerySet(models.QuerySet):
    def check_and_update(self):
        # Collect IDs of items to be deleted
        ids_to_delete = []

        # Iterate over the queryset
        for item in self:
            if not item.check_and_update_quantity(force_save=False):
                ids_to_delete.append(item.id)

        # Remove deleted items from the queryset
        if ids_to_delete:
            self = self.exclude(id__in=ids_to_delete)

        return self

    def check_and_update_items(self):
        return self.check_and_update()


class CartItemManager(models.Manager):
    def get_queryset(self):
        return CartItemQuerySet(self.model, using=self._db)

    def check_and_update_items(self):
        return self.get_queryset().check_and_update()


class CartItem(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    product = models.ForeignKey(
        Product, related_name="product_carts", on_delete=models.CASCADE
    )
    product_option_id = models.CharField(
        max_length=225, default=uuid.uuid4, db_index=True
    )
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.FloatField(blank=False)
    charge = models.FloatField(blank=False, default=0.00)
    cart = models.ForeignKey(
        Cart, related_name="cart_item", on_delete=models.CASCADE, null=True
    )
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE, null=True
    )
    ordered = models.BooleanField(default=False)

    objects = CartItemManager()

    def __str__(self):
        return f"{self.product.product_title} - {self.product.user}"

    def check_and_update_quantity(self, force_save=True):
        try:
            product_option = ProductOption.objects.get(id=self.product_option_id)
        except ProductOption.DoesNotExist:
            self.delete()
            return False

        print("product_option.quantity", product_option.quantity, self.quantity)
        if int(product_option.quantity) < 1:
            self.delete()
            return False
        elif self.quantity > int(product_option.quantity):
            self.quantity = int(product_option.quantity)
            if force_save:
                self.save()

        return True


class Wishlist(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    user = models.ForeignKey(User, related_name="user_wish", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class WishListItem(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    product = models.ForeignKey(
        Product, related_name="products_wished", on_delete=models.CASCADE
    )
    wishlist = models.ForeignKey(
        Wishlist, related_name="wishlist_item", on_delete=models.CASCADE
    )


class FlashSales(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    product = models.ForeignKey(ProductOption, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    number_of_days = models.IntegerField(default=1)
    discount_percent = models.FloatField(default=1)
    status = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.id} - {self.number_of_days}"


class StateDeliveryFee(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    state = models.CharField(max_length=255, blank=False)
    city = models.CharField(max_length=255, blank=True)
    fee = models.FloatField(default=0.00)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["state"], name="state_idx"),
            models.Index(fields=["city"], name="city_idx"),
        ]

    def __str__(self):
        return f"{self.state} - {self.city}"


class ProductCharge(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    has_fixed_amount = models.BooleanField(default=False)
    charge = models.FloatField(default=0.00)


nigerian_states = [
    "abia",
    "adamawa",
    "akwa ibom",
    "anambra",
    "bauchi",
    "bayelsa",
    "benue",
    "borno",
    "cross river",
    "delta",
    "ebonyi",
    "edo",
    "ekiti",
    "enugu",
    "gombe",
    "imo",
    "jigawa",
    "kaduna",
    "kano",
    "katsina",
    "kebbi",
    "kogi",
    "kwara",
    "lagos",
    "nasarawa",
    "niger",
    "ogun",
    "ondo",
    "osun",
    "oyo",
    "plateau",
    "rivers",
    "sokoto",
    "taraba",
    "yobe",
    "zamfara",
    "abuja",
]


def get_delivery_fee(state: str, city: str) -> float:
    fee = get_delivery_fee_obj(state, city)
    if fee:
        return fee.fee
    return 0


def get_delivery_fee_obj(state: str, city: str) -> StateDeliveryFee:
    city_fee = None
    if not city or city == "":
        city_fee = (
            StateDeliveryFee.objects.filter(state__iexact=state)
            .exclude(city__isnull=True)
            .exclude(city__exact="")
        )
    else:
        city_fee = StateDeliveryFee.objects.filter(
            state__iexact=state, city__iexact=city
        )

    if city_fee.exists():
        return city_fee[0]
    else:
        state_fee = (
            StateDeliveryFee.objects.filter(state__iexact=state)
            .exclude(city__isnull=True)
            .exclude(city__exact="")
        )
        print("STATE", state_fee)
        if state_fee.exists():
            return state_fee[0]
        else:
            state_fee = StateDeliveryFee.objects.filter(state__iexact=state)
            if state_fee.exists():
                return state_fee[0]
            else:
                return None


def update_state_delivery_fees():
    default_fee = 0.00

    for state in nigerian_states:
        if StateDeliveryFee.objects.filter(state__iexact=state).exists():
            print(f"Delivery fee for {state} already exists")

        created = StateDeliveryFee.objects.create(state=state, fee=default_fee)
        if created:
            print(f"Created delivery fee for {state}")
        else:
            print(f"Delivery fee for {state} already exists")
