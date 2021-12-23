from graphene_django import DjangoObjectType

from .models import (
    Billing,
    Payment,
    Pickups
)



class BillingType(DjangoObjectType):
    class Meta:
        model = Billing
        fields = "__all__"

        

class PickupType(DjangoObjectType):
    class Meta:
        model = Pickups
        fields = "__all__"

class PaymentType(DjangoObjectType):
    class Meta:
        model = Payment
        fields = "__all__"