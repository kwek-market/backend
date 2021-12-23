import graphene
import jwt

from django.conf import settings
from users.models import ExtendUser
from .models import (
    Billing,
    Payment,
    Pickups
)
from .object_types import (
    BillingType,
    PaymentType,
    PickupType
)



class BillingAddress(graphene.Mutation):
    billing_address = graphene.Field(BillingType)
    status = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        contact = graphene.String(required=True)
        address = graphene.String(required=True)
        state = graphene.String(required=True)
        city = graphene.String(required=True)
        token = graphene.String()
    
    @staticmethod
    def mutate(self, root, first_name, last_name, contact, address, state, city, token=None):
        billing_address = Billing.objects.filter(full_name=f"{first_name} {last_name}", contact=contact, location=f"{address} {state} {city}")
        if billing_address.exists():
            return BillingAddress(billing_address=billing_address, status=True, message="Address added")
        else:
            if token is None:
                billing_address = Billing.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    contact=contact,
                    address=address,
                    state = state,
                    city=city
                )
                return BillingAddress(billing_address=billing_address, status=True, message="Address added")
            elif token is not None:
                email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
                user = ExtendUser.objects.get(email=email)
                if user:
                    billing_address = Billing.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        contact=contact,
                        address=address,
                        state = state,
                        city=city,
                        user=user
                    )
                    return BillingAddress(billing_address=billing_address, status=True, message="Address added")
                
                else:
                    return {
                        "status": False,
                        "message": "Invalid User"
                    }
            else:
                return {
                    "status": False,
                    "message": "Address not added"
                }


class PickUpLocation(graphene.Mutation):
    location = graphene.Field(PickupType)
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        contact = graphene.String(required=True)
        address = graphene.String(required=True)
        state = graphene.String(required=True)
        city = graphene.String(required=True)
    
    @staticmethod
    def mutate(self, root, name, contact, address, state, city):
        location = Pickups.objects.filter(name=name)
        if location.exists():
            return {
                "status": False,
                "message": f"Location {name} already exists"
            }
        else:
            try:
                location = Pickups.objects.create(
                    name=name,
                    contact=contact,
                    address=address,
                    state=state,
                    city=city
                )
                return PickUpLocation(location=location, status=True, message="Location added")
            except Exception as e:
                return {
                    "status": False,
                    "message": e
                }

class PaymentInitiate(graphene.Mutation):
    payment = graphene.Field(PaymentType)
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        amount = graphene.Int(required=True)
        email = graphene.String(required=True)
    
    @staticmethod
    def mutate(self, info, amount, email):
        if amount and email:
            try:
                payment = Payment.objects.create(amount=amount, email=email)
                payment.save()
                return PaymentInitiate(
                    payment=payment,
                    status=True,
                    message="Payment Successful"
                )
            except Exception as e:
                return {
                    "status": False,
                    "message": e
                }
        else:
            return {
                "status": False,
                "message": "Invalid amount or email"
            }

        pass