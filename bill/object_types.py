from django.db.models import fields
from graphene_django import DjangoObjectType

from .models import (
    Billing,
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