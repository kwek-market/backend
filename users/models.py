from typing import Any, Dict, List
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.db.models import Sum, F, FloatField, Q

# Create your models here.


class ExtendUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(
        blank=False, max_length=255, verbose_name="email", unique=True, db_index=True
    )
    full_name = models.CharField(blank=False, max_length=255, verbose_name="full_name")
    phone_number = models.CharField(
        blank=True, max_length=255, verbose_name="full_name", db_index=True
    )
    is_verified = models.BooleanField(default=False, verbose_name="is_verified")
    is_seller = models.BooleanField(default=False, verbose_name="is_seller")
    is_admin = models.BooleanField(default=False, verbose_name="is_admin" )
    is_flagged = models.BooleanField(default=False, verbose_name="red_flagged")

    USERNAME_FIELD = "username"
    EmailField = "email"

    @classmethod
    def get_emails_by_ids(cls, ids:List[str])->List[str]:
        return list(cls.objects.filter(id__in=ids).values_list('email', flat=True))
    
    @classmethod
    def get_users_dict_by_ids(cls, ids: List[str]) -> Dict[str, Dict]:
        users = cls.objects.filter(id__in=ids)
        return {str(user.id): user.to_representation() for user in users}

    def get_total_spent(self):
        total_spent = self.order.filter(paid=True).aggregate(
            total=Sum(
                F('order_price_total') - 
                F('walletrefund__number_of_product') * 
                F('walletrefund__product__price'),
                output_field=FloatField(),
                filter=Q(walletrefund__status=True)
            )
        )['total']
        return total_spent if total_spent else 0

    def to_representation(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'is_verified': self.is_verified,
            'is_seller': self.is_seller,
            'is_admin': self.is_admin,
            'is_flagged': self.is_flagged,
            'username': self.username,
            'email': self.email,
            'is_staff': self.is_staff,
            'is_active': self.is_active,
            'date_joined': self.date_joined,
            'total_spent': self.get_total_spent()
        }
        


class SellerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(ExtendUser, related_name="seller_profile", on_delete=models.CASCADE, null=True)
    firstname = models.CharField(max_length=255, blank=False, null=True, db_index=True)
    lastname = models.CharField(max_length=255, blank=False, null=True, db_index=True)
    phone_number = models.CharField(max_length=255, blank=False, null=True)
    shop_name = models.CharField(max_length=255, blank=False, null=True, db_index=True)
    shop_url = models.CharField(max_length=255, blank=False, null=True, db_index=True)
    shop_address = models.CharField(max_length=255, blank=False, null=True)
    state = models.CharField(max_length=255, blank=False, null=True, db_index=True)
    city = models.CharField(max_length=255, blank=True, null=True, db_index=True)
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
    seller_is_rejected = models.BooleanField(
        default=False, verbose_name="seller_is_rejected"
    )
    bank_account_is_verified = models.BooleanField(
        default=False, verbose_name="bank_account_is_verified"
    )
    accepted_vendor_policy = models.BooleanField(
        default=False, verbose_name="accepted_vendor_policy"
    )


    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.full_name
    
    @property
    def since(self):
      return (timezone.now() - self.date).days

class SellerCustomer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    seller = models.OneToOneField(SellerProfile, on_delete=models.CASCADE, related_name="customers")
    customer_id = ArrayField(models.CharField(max_length=225), blank=True, default=list)
    date_created = models.DateTimeField(auto_now_add=True)
