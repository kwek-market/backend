from typing import Dict
import graphene
from graphene_django import DjangoObjectType
from users.models import SellerCustomer, SellerProfile
from django.contrib.auth import get_user_model


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class SellerProfileType(DjangoObjectType):
    class Meta:
        model = SellerProfile
        fields = (
            "id",
            "user",
            "firstname",
            "lastname",
            "phone_number",
            "shop_name",
            "shop_url",
            "shop_address",
            "state",
            "city",
            "lga",
            "landmark",
            "how_you_heard_about_us",
            "accepted_policy",
            "store_banner_url",
            "store_description",
            "prefered_id",
            "prefered_id_url",
            "bvn",
            "bank_name",
            "bank_account_number",
            "bank_account_name",
            "seller_is_verified",
            "bank_account_is_verified",
            "bank_sort_code",
            "accepted_vendor_policy",
        )

class SellerCustomerType(DjangoObjectType):

    days_selling = graphene.Int()
    
    @staticmethod
    def resolve_days_selling(parent, info, *args, **kwargs):
        days = SellerProfile.objects.get(user=parent.user).since
        return [days]
    class Meta:
        model = SellerCustomer
    