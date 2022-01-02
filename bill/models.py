import uuid
import secrets
from django.db import models

from users.models import ExtendUser
# Create your models here.


class Billing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=13)
    address = models.CharField(max_length=355)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    user = models.ForeignKey(ExtendUser, null=True, on_delete=models.CASCADE)


    def __str__(self) -> str:
        return self.first_name

    @property
    def location(self) -> str:
        return f"{self.address} {self.state} {self.city}"


    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Pickups(models.Model):
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
    
    def amount_value(self) -> int:
        return self.amount*100
