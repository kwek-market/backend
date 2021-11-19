from graphene_django import DjangoObjectType, DjangoListField
import graphene
from .models import *


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"


class KeywordType(DjangoObjectType):
    class Meta:
        model = Keyword
        fields = ("id", "keyword")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        fields = (
            "id",
            "product_title",
            "user",
            "category",
            "brand",
            "product_weight",
            "short_description",
            "charge_five_percent_vat",
            "return_policy",
            "warranty",
            "color",
            "gender",
            "keyword",
            "options",
            "clicks",
            "promoted",
        )
        filter_fields = {
            "id": ["exact"],
            "product_title": ["exact", "icontains"],
            "color": ["exact", "iexact"],
            "brand": ["exact", "iexact"],
            "gender": ["exact", "iexact", "istartswith"],
            "short_description": ["exact", "icontains"],
            "keyword__keyword": ["exact", "icontains", "istartswith"],
        }


class ProductImageType(DjangoObjectType):
    class Meta:
        model = ProductImage
        fields = ("id", "product", "image_url")


class ProductOptionType(DjangoObjectType):
    class Meta:
        model = ProductOption
        fields = (
            "id",
            "product",
            "size",
            "quantity",
            "price",
            "discounted_price",
            "option_total_price",
        )


class ProductPromotionType(DjangoObjectType):
    class Meta:
        model = ProductPromotion
        fields = (
            "id",
            "product",
            "start_date",
            "end_date",
            "days",
            "active",
            "amount",
            "reach",
            "link_clicks",
        )

class RatingType(DjangoObjectType):
    class Meta:
        model = Rating
        fields = ("id", "product", "rating", "comment", "name", "email", "rated_at")

class NewsletterType(DjangoObjectType):
    class Meta:
        model = Newsletter
        fields = "__all__"

class CartType(DjangoObjectType):
    class Meta:
        model = Cart

class WishlistType(DjangoObjectType):
    class Meta:
        model = Wishlist
