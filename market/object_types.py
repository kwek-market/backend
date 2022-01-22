import graphene
from graphene.relay.connection import Connection
from graphene_django import DjangoObjectType

from bill.models import Order
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
        fields = "__all__"

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
        fields = "__all__"

class NewsletterType(DjangoObjectType):
    class Meta:
        model = Newsletter
        fields = "__all__"


class ContactMessageType(DjangoObjectType):
    class Meta:
        model = ContactMessage
        fields = "__all__"



class CartType(DjangoObjectType):
    class Meta:
        model = Cart

class CartItemType(DjangoObjectType):
    class Meta:
        model = CartItem
class WishlistType(DjangoObjectType):
    class Meta:
        model = Wishlist

class WishlistItemType(DjangoObjectType):
    class Meta:
        model = WishListItem
class OrderType(DjangoObjectType):
    class Meta:
        model=Order