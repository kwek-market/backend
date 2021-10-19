from graphene_django import DjangoObjectType
from users.models import SellerProfile
from django.contrib.auth import get_user_model


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class SellerProfileType(DjangoObjectType):
    class Meta:
        model = SellerProfile
        fields = (
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
