import pytest
from django.contrib.auth import get_user_model
from bill.models import Billing, Pickup, Payment
from users.models import ExtendUser

User = get_user_model()


@pytest.mark.django_db
def test_billing_address_success(client, valid_token, user):
    mutation = """
        mutation BillingAddress($fullName: String!, $contact: String!, $address: String!, $state: String!, $city: String!, $token: String) {
            billingAddress(fullName: $fullName, contact: $contact, address: $address, state: $state, city: $city, token: $token) {
                status
                message
                billingAddress {
                    id
                    fullName
                    contact
                    address
                    state
                    city
                }
            }
        }
    """
    variables = {
        "fullName": "John Doe",
        "contact": "1234567890",
        "address": "123 Test Street",
        "state": "Test State",
        "city": "Test City",
        "token": valid_token,
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["billingAddress"]["status"] is True
    assert response["data"]["billingAddress"]["message"] == "Address added"
    assert (
        response["data"]["billingAddress"]["billingAddress"]["fullName"] == "John Doe"
    )


@pytest.mark.django_db
def test_billing_address_update_success(client, valid_token, user):
    billing_address = Billing.objects.create(
        full_name="John Doe",
        contact="1234567890",
        address="123 Test Street",
        state="Test State",
        city="Test City",
        user=user,
    )
    mutation = """
        mutation BillingAddressUpdate($addressId: String!, $fullName: String, $contact: String, $address: String, $state: String, $city: String) {
            billingAddressUpdate(addressId: $addressId, fullName: $fullName, contact: $contact, address: $address, state: $state, city: $city) {
                status
                message
                billing {
                    id
                    fullName
                    contact
                    address
                    state
                    city
                }
            }
        }
    """
    variables = {
        "addressId": str(billing_address.id),
        "fullName": "Jane Doe",
        "contact": "0987654321",
        "address": "456 New Street",
        "state": "New State",
        "city": "New City",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["billingAddressUpdate"]["status"] is True
    assert (
        response["data"]["billingAddressUpdate"]["message"]
        == "Address updated successfully"
    )
    assert response["data"]["billingAddressUpdate"]["billing"]["fullName"] == "Jane Doe"


@pytest.mark.django_db
def test_billing_address_delete_success(client, valid_token, user):
    billing_address = Billing.objects.create(
        full_name="John Doe",
        contact="1234567890",
        address="123 Test Street",
        state="Test State",
        city="Test City",
        user=user,
    )
    mutation = """
        mutation BillingAddressDelete($addressId: String!) {
            billingAddressDelete(addressId: $addressId) {
                status
                message
            }
        }
    """
    variables = {
        "addressId": str(billing_address.id),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["billingAddressDelete"]["status"] is True
    assert (
        response["data"]["billingAddressDelete"]["message"]
        == "Address deleted successfully"
    )
    assert not Billing.objects.filter(id=billing_address.id).exists()


@pytest.mark.django_db
def test_pickup_location_success(client):
    mutation = """
        mutation PickUpLocation($name: String!, $contact: String!, $address: String!, $state: String!, $city: String!) {
            pickUpLocation(name: $name, contact: $contact, address: $address, state: $state, city: $city) {
                status
                message
                location {
                    id
                    name
                    contact
                    address
                    state
                    city
                }
            }
        }
    """
    variables = {
        "name": "Test Location",
        "contact": "1234567890",
        "address": "123 Test Street",
        "state": "Test State",
        "city": "Test City",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["pickUpLocation"]["status"] is True
    assert response["data"]["pickUpLocation"]["message"] == "Location added"
    assert response["data"]["pickUpLocation"]["location"]["name"] == "Test Location"


@pytest.mark.django_db
def test_pickup_location_update_success(client):
    pickup_location = Pickup.objects.create(
        name="Test Location",
        contact="1234567890",
        address="123 Test Street",
        state="Test State",
        city="Test City",
    )
    mutation = """
        mutation PickupLocationUpdate($addressId: String!, $name: String, $contact: String, $address: String, $state: String, $city: String) {
            pickupLocationUpdate(addressId: $addressId, name: $name, contact: $contact, address: $address, state: $state, city: $city) {
                status
                message
            }
        }
    """
    variables = {
        "addressId": str(pickup_location.id),
        "name": "Updated Location",
        "contact": "0987654321",
        "address": "456 New Street",
        "state": "New State",
        "city": "New City",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["pickupLocationUpdate"]["status"] is True
    assert (
        response["data"]["pickupLocationUpdate"]["message"]
        == "Address updated successfully"
    )
    updated_location = Pickup.objects.get(id=pickup_location.id)
    assert updated_location.name == "Updated Location"


@pytest.mark.django_db
def test_pickup_location_delete_success(client):
    pickup_location = Pickup.objects.create(
        name="Test Location",
        contact="1234567890",
        address="123 Test Street",
        state="Test State",
        city="Test City",
    )
    mutation = """
        mutation PickupLocationDelete($addressId: String!) {
            pickupLocationDelete(addressId: $addressId) {
                status
                message
            }
        }
    """
    variables = {
        "addressId": str(pickup_location.id),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["pickupLocationDelete"]["status"] is True
    assert (
        response["data"]["pickupLocationDelete"]["message"]
        == "Address deleted successfully"
    )
    assert not Pickup.objects.filter(id=pickup_location.id).exists()


@pytest.mark.django_db
def test_payment_initiate_success(client, valid_token, user):
    mutation = """
        mutation PaymentInitiate($amount: Float!, $token: String!, $description: String!, $redirectUrl: String!, $currency: String, $gateway: String!) {
            paymentInitiate(amount: $amount, token: $token, description: $description, redirectUrl: $redirectUrl, currency: $currency, gateway: $gateway) {
                status
                message
                payment {
                    id
                    amount
                    description
                }
                paymentLink
            }
        }
    """
    variables = {
        "amount": 100.0,
        "token": valid_token,
        "description": "Test Payment",
        "redirectUrl": "https://example.com/redirect",
        "currency": "NGN",
        "gateway": "gateway",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["paymentInitiate"]["status"] is True
    assert response["data"]["paymentInitiate"]["payment"]["amount"] == 100.0
    assert (
        response["data"]["paymentInitiate"]["payment"]["description"] == "Test Payment"
    )


@pytest.mark.django_db
def test_payment_verification_success(client, valid_token, user):
    payment = Payment.objects.create(
        amount=100.0,
        user=user,
        email=user.email,
        name=user.full_name,
        phone=user.phone_number,
        description="Test Payment",
        gateway="gateway",
        ref="valid_ref",
    )
    mutation = """
        mutation PaymentVerification($transactionRef: String!, $transactionId: String!) {
            paymentVerification(transactionRef: $transactionRef, transactionId: $transactionId) {
                status
                message
                transactionInfo
            }
        }
    """
    variables = {
        "transactionRef": "valid_ref",
        "transactionId": "valid_id",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["paymentVerification"]["status"] is True
    assert response["data"]["paymentVerification"]["message"] == "Payment verified"
    assert Payment.objects.get(ref="valid_ref").verified is True
