import graphene
from graphene_django import DjangoObjectType

from bill.models import Order
from bill.object_types import GetSellerOrdersType
from .models import *
from users.model_object_type import UserType


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"
        convert_choices_to_enum = False


class KeywordType(DjangoObjectType):
    class Meta:
        model = Keyword
        fields = ("id", "keyword") 


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class FlashSalesType(DjangoObjectType):
    class Meta:
        model = FlashSales
        fields = "__all__"
class ProductChargeType(DjangoObjectType):
    class Meta:
        model = ProductCharge
        fields = "__all__"
class StateDeliveryType(DjangoObjectType):
    class Meta:
        model = StateDeliveryFee
        fields = "__all__"

class ProductImageType(DjangoObjectType):
    class Meta:
        model = ProductImage
        fields = ("id", "product", "image_url")


class ProductOptionType(DjangoObjectType):
    price = graphene.Float()
    discounted_price = graphene.Float()
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
            "quantity"
        )
    def resolve_price(self, info):
        return self.get_product_price()
    def resolve_discounted_price(self, info):
        return self.get_product_discounted_price()


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
            "balance",
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

class SalesType(DjangoObjectType):
    class Meta:
        model = Sales

class ProductPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(ProductType)

class RatingPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(RatingType)

class FlashSalesPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(FlashSalesType)


class GetSellerOrdersPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()                                     
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(GetSellerOrdersType)


class DeliveryFeeType(graphene.ObjectType):
    id = graphene.String()
    city = graphene.String() 
    fee = graphene.Float()

class StateDeliveryFeeType(graphene.ObjectType):
    state = graphene.String()
    delivery_fees = graphene.List(DeliveryFeeType)