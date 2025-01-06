import graphene
from graphene_django import DjangoObjectType
from users.model_object_type import UserType

from .models import (
    Billing,
    Coupon,
    Order,
    Payment,
    Pickup
)


class OrderType(DjangoObjectType):
    class Meta:
        model=Order
        fields = "__all__"

class OrderPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(OrderType)

class GetSellerOrdersType(graphene.ObjectType):
    order = graphene.Field(OrderType)
    created = graphene.String()
    customer = graphene.Field(UserType)
    total = graphene.Int()
    profit = graphene.Int()
    paid = graphene.Boolean()
    status = graphene.String()

class BillingType(DjangoObjectType):
    class Meta:
        model = Billing
        fields = "__all__"

        

class PickupType(DjangoObjectType):
    class Meta:
        model = Pickup
        fields = "__all__"

class PaymentType(DjangoObjectType):
    class Meta:
        model = Payment
        fields = "__all__"

class CouponType(DjangoObjectType):
    class Meta:
        model = Coupon

class CouponPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(CouponType)