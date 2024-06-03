import graphene
from graphene_django import DjangoObjectType

from .models import (
    Billing,
    Coupon,
    Payment,
    Pickup
)



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