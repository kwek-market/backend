from graphene_django import DjangoObjectType

from .models import (
    Billing,
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