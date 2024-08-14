import uuid
import secrets
import string
from django.apps import apps
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from users.models import ExtendUser
from django.db import transaction
# Create your models here.


class Billing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    full_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=15)
    address = models.CharField(max_length=355)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    user = models.ForeignKey(ExtendUser, null=True, on_delete=models.CASCADE)


    def __str__(self) -> str:
        return self.full_name

    @property
    def location(self) -> str:
        return f"{self.address} {self.state} {self.city}"



class Pickup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=13)
    address = models.CharField(max_length=355)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name
    
    @property
    def location(self) -> str:
        return f"{self.address} {self.state} {self.city}"


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    amount = models.FloatField(default=0)
    ref = models.CharField(max_length=200)
    user_id = models.CharField(max_length=225, default=None)
    gateway = models.CharField(max_length=225, default="flutterwave")
    email = models.EmailField(blank=False)
    name = models.CharField(max_length=225, default="admin")
    phone = models.CharField(max_length=15, default="+1809384583")
    description = models.CharField(max_length=225, default="Purchase goods")
    currency = models.CharField(max_length=3, default="USD")
    verified = models.BooleanField(default=False)
    redirect_url = models.URLField(default="https://kwekmarket.com/")
    transaction_date = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ("-transaction_date",)
    
    def __str__(self) -> str:
        return f"Payment {self.amount}"

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Payment.objects.filter(ref=ref)

            if not object_with_similar_ref.exists():
                self.ref = ref
        super().save(*args, **kwargs)



class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=10, help_text="If left blank, it will be created automatically", unique=True)
    value = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    user_list = ArrayField(models.CharField(max_length=225), blank=True, null=True)

    def save(self, *args, **kwargs):

        while not self.code:
            alpha_num = string.ascii_uppercase + string.digits
            random_code = "".join(secrets.choice(alpha_num) for i in range(5))
            code = f"KW-{random_code}"
            object_with_similar_code = Coupon.objects.filter(code=code)
            if not object_with_similar_code.exists():
                self.code = code
        super().save(*args, **kwargs)
    
    
    
    @property
    def expired(self):
        return self.valid_until is not None and self.valid_until < timezone.now()

    @property
    def user_limit(self):
        """ Returns lenght of user_list if coupon is bound to specific user(s) """
        if self.user_list:
            return len(self.user_list)
        else:
            return 0

    @property
    def is_redeemed(self):
        """ Returns true is a coupon is redeemed (completely for all users) otherwise returns false. """
        return self.users.filter(
            redeemed_at__isnull=False
        ).count() >= self.user_limit and self.user_limit != 0
    
    @property
    def redeemed_at(self):
        try:
            return self.users.filter(redeemed_at__isnull=False).order_by('redeemed_at').last().redeemed_at
        except self.users.through.DoesNotExist:
            return None
    
    def redeem(self, user=None):
        try:
            coupon_user = self.users.get(user=user)
        except CouponUser.DoesNotExist:
            try:  # silently fix unbouned or nulled coupon users
                coupon_user = self.users.get(user__isnull=True)
                coupon_user.user = user
            except CouponUser.DoesNotExist:
                coupon_user = CouponUser(coupon=self, user=user)
        coupon_user.redeemed_at = timezone.now()
        coupon_user.save()


class CouponUser(models.Model):
    coupon = models.ForeignKey(Coupon, related_name="users", on_delete=models.CASCADE)
    user = models.ForeignKey(ExtendUser, on_delete=models.CASCADE, null=True, blank=True)
    redeemed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (("coupon", "user"))
    
    def __str__(self) -> str:
        return super().__str__(self.user)
    

class OrderProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    progress = models.CharField(max_length=30, default="Order Placed")
    order = models.OneToOneField("Order", on_delete=models.CASCADE, related_name="progress")

    def __str__(self) -> str:
        return self.order.order_id
   
   

class OrderManager(models.Manager):
    def create(self, **kwargs):
        # Extract and remove cart_items from kwargs if present
        cart_items = kwargs.pop('cart_items', None)

        order = self.model(**kwargs)
        total_coupon_price = 0

        if order.coupon:
            for id in order.coupon:
                coupon_item = Coupon.objects.get(id=id)
                total_coupon_price += int(coupon_item.value)

        with transaction.atomic():
            while not order.order_id:
                order_id = f"KWEK-{secrets.token_urlsafe(8)}"
                if not Order.objects.filter(order_id=order_id).exists():
                    order.order_id = order_id

            order.save()
            # Transfer CartItems from Cart to Order
            if cart_items is None:
                CartItem = apps.get_model('market', 'CartItem')
                cart_items = CartItem.objects.filter(cart__user=order.user, ordered=False)
            order.cart_items.set(cart_items)
            cart_items.update(ordered=True, cart=None, order=order)


            order_price = 0
            for cart_item in order.cart_items.all():
                order_price += (cart_item.quantity * cart_item.price)

            first_order_price = order_price

            if total_coupon_price > 0:
                order_price = order_price - total_coupon_price
                if order_price < 0:
                    order_price = 0

            if order.delivery_fee > 0:
                order_price += order.delivery_fee

            order_price_total = order_price

            Order.objects.filter(id=order.id).update(order_price=first_order_price, order_price_total=order_price_total)

        return order
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(ExtendUser, related_name="order", on_delete=models.CASCADE)
    order_id = models.CharField(max_length=30)
    cart_items = models.ManyToManyField('market.CartItem',related_name='order_cart_items')
    payment_method = models.CharField(max_length=30)
    delivery_method = models.CharField(max_length=30)
    delivery_status = models.CharField(max_length=30, default="Order in progress")
    closed = models.BooleanField(default=False)
    coupon = ArrayField(models.CharField(max_length=225), blank=True, null=True)
    paid = models.BooleanField(default=False)
    door_step = models.ForeignKey(Billing, on_delete=models.CASCADE, null=True)
    pickup = models.ForeignKey(Pickup, on_delete=models.CASCADE, null=True)
    order_price = models.PositiveBigIntegerField(default=0)
    order_price_total = models.PositiveBigIntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    delivery_fee = models.FloatField(blank=False, null=False, default=0.00)

    # def save(self, *args, **kwargs):
    #     print("saving order", self.id)
    #     print("delivery fee", self.delivery_fee)
    #     total_coupon_price = 0

    #     if self.coupon:
    #         for id in self.coupon:
    #             coupon_item = Coupon.objects.get(id=id)
    #             total_coupon_price += int(coupon_item.value)
    #     print("total_coupon_price", total_coupon_price)
    #     print("pk", self.pk)

    #     with transaction.atomic():
    #         if not self.pk:  # Only if it's a new order
    #             print("no self .pk")
    #             while not self.order_id:
    #                 order_id = f"KWEK-{secrets.token_urlsafe(8)}"
    #                 if not Order.objects.filter(order_id=order_id).exists():
    #                     self.order_id = order_id

    #             super().save(*args, **kwargs)

    #             # Transfer CartItems from Cart to Order
    #             if not self.cart_items.exists():
    #                 CartItem = apps.get_model('market', 'CartItem')
    #                 cart_items = CartItem.objects.filter(cart__user=self.user, ordered=False)
    #                 self.cart_items.set(cart_items)
    #                 cart_items.update(ordered=True, cart=None, order=self)

    #             print("order cart items", self.cart_items.all())

    #             order_price = 0
    #             if self.cart_items.exists():
    #                 for cart_item in self.cart_items.all():
    #                     order_price += (cart_item.quantity * cart_item.price)
                
    #             first_order_price = order_price
    #             print("first_order_price", first_order_price)

    #             if total_coupon_price > 0:
    #                 order_price = order_price - total_coupon_price
    #                 if order_price < 0:
    #                     order_price = 0

    #             if self.delivery_fee > 0:
    #                 order_price += self.delivery_fee

    #             order_price_total = order_price
    #             print("order_price_total", order_price_total)

    #             Order.objects.filter(id=self.id).update(order_price=first_order_price,order_price_total=order_price_total)
    #             print("self first_order_price", self.order_price)
    #             print("self order_price_total", self.order_price_total)
    #             # super().save(*args, **kwargs) // apparently you cannot call this twice, it will be like calling create multiple times
    #     if self.pk:
    #         print("has self .pk")
    #         super().save(*args, **kwargs)

    #     print("end delivery fee", self.delivery_fee)
    #     print("end order cart items", self.cart_items.all())
    #     print("end self first_order_price", self.order_price)
    #     print("end self order_price_total", self.order_price_total)

    objects = OrderManager()
    def __str__(self) -> str:
        return self.order_id
    
    class Meta:
        indexes = [
            models.Index(fields=["-date_created"])
        ]
