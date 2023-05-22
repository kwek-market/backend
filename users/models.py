import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

# Create your models here.


class ExtendUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(
        blank=False, max_length=255, verbose_name="email", unique=True
    )
    full_name = models.CharField(blank=False, max_length=255, verbose_name="full_name")
    phone_number = models.CharField(
        blank=True, max_length=255, verbose_name="full_name"
    )
    is_verified = models.BooleanField(default=False, verbose_name="is_verified")
    is_seller = models.BooleanField(default=False, verbose_name="is_seller")
    is_admin = models.BooleanField(default=False, verbose_name="is_admin" )

    USERNAME_FIELD = "username"
    EmailField = "email"


class SellerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
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
    kwek_charges = models.FloatField(default=0.1)
    store_banner_url = models.CharField(max_length=255, blank=True, null=True)
    store_description = models.CharField(max_length=255, blank=True, null=True)
    prefered_id = models.CharField(max_length=255, blank=True, null=True)
    prefered_id_url = models.CharField(max_length=255, blank=True, null=True)
    bvn = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_sort_code = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=255, blank=True, null=True)
    bank_account_name = models.CharField(max_length=255, blank=True, null=True)
    seller_is_verified = models.BooleanField(
        default=False, verbose_name="seller_is_verified"
    )
    bank_account_is_verified = models.BooleanField(
        default=False, verbose_name="bank_account_is_verified"
    )
    accepted_vendor_policy = models.BooleanField(
        default=False, verbose_name="accepted_vendor_policy"
    )


    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user
    
    @property
    def since(self):
      return (timezone.now() - self.date).days

class SellerCustomer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    seller = models.OneToOneField(SellerProfile, on_delete=models.CASCADE, related_name="customers")
    customer_id = ArrayField(models.CharField(max_length=225))
    date_created = models.DateTimeField(auto_now_add=True)
