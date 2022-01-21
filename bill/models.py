import uuid
import secrets
from django.db import models
from django.contrib.postgres.fields import ArrayField
from users.models import ExtendUser
from market.models import Cart, Product
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
    amount = models.FloatField()
    ref = models.CharField(max_length=200)
    user_id = models.CharField(max_length=225, default=None)
    email = models.EmailField()
    name = models.CharField(max_length=225, default="admin")
    phone = models.CharField(max_length=15, default="+1809384583")
    description = models.CharField(max_length=225, default="Purchase goods")
    currency = models.CharField(max_length=3, default="USD")
    verified = models.BooleanField(default=False)
    redirect_url = models.URLField(default="https://kwekmarket.com/")
    transaction_date = models.DateTimeField(auto_now_add=True)

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
    code = models.CharField(max_length=7)
    amount = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        while not self.code:
            code = f"KW-{secrets.token_urlsafe(4)}"

            object_with_similar_code = Coupon.objects.filter(code=code)
            if not object_with_similar_code.exists():
                self.code = code
        super().save(*args, **kwargs)
    
    class Meta:
        abstract = True

class ProductCoupon(Coupon):
    pass

class OrderCoupon(Coupon):
    pass

class UsedCoupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    coupon_type = models.CharField(max_length=20)
    user = models.ForeignKey(ExtendUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.coupon_type == "product":
            coupon = models.ForeignKey(Product, on_delete=models.CASCADE)
            self.coupon = coupon
        elif self.coupon_type == "order":
            coupon = models.ForeignKey(Order, on_delete=models.CASCADE)
            self.coupon = coupon
        super().save(*args, **kwargs)

class OrderProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    progress = models.CharField(max_length=30, default="Order Placed")
    order = models.OneToOneField("Order", on_delete=models.CASCADE)
    

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(ExtendUser, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=30)
    cart_items = ArrayField(models.CharField(max_length=225), default=None)
    payment_method = models.CharField(max_length=30)
    delivery_method = models.CharField(max_length=30)
    delivery_status = models.CharField(max_length=30, default="Order in progress")
    closed = models.BooleanField(default=False)
    ordercoupon = models.ForeignKey(OrderCoupon, on_delete=models.CASCADE, null=True)
    productcoupon = models.ForeignKey(ProductCoupon, on_delete=models.CASCADE, null=True)
    door_step = models.ForeignKey(Billing, on_delete=models.CASCADE, null=True)
    pickup = models.ForeignKey(Pickup, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        while not self.order_id:
            order_id = f"KWEK-{secrets.token_urlsafe(14)}"

            object_with_similar_order_id = Order.objects.filter(order_id=order_id)
            if not object_with_similar_order_id.exists():
                self.order_id = order_id
        
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.order_id
