import secrets
import string
import uuid
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model

from bill.models import Billing, Payment, Pickup

User = get_user_model()


@pytest.mark.django_db
class TestBillingMutations:
    def test_billing_address_success(self, client, valid_token, user, billing_mutation):
        variables = {
            "fullName": "John Doe",
            "contact": "1234567890",
            "address": "123 Test Street",
            "state": "Test State",
            "city": "Test City",
            "token": valid_token,
        }

        response = client.execute(billing_mutation, variables=variables)

        assert response is not None
        assert "data" in response
        assert "billingAddress" in response["data"]
        result = response["data"]["billingAddress"]

        assert result["status"] is True
        assert result["message"] == "Address added"
        assert result["billingAddress"]["fullName"] == "John Doe"

    def test_billing_address_update_success(
        self, client, valid_token, user, billing_mutation
    ):
        # First create the address
        variables = {
            "fullName": "John Doe",
            "contact": "1234567890",
            "address": "123 Test Street",
            "state": "Test State",
            "city": "Test City",
            "token": valid_token,
        }

        client.execute(billing_mutation, variables=variables)

        # Try to create same address again
        response = client.execute(billing_mutation, variables=variables)

        assert response is not None
        assert "data" in response
        assert "billingAddress" in response["data"]
        result = response["data"]["billingAddress"]

        assert result["status"] is True
        assert result["message"] == "Address retrieved"
        assert result["billingAddress"]["fullName"] == "John Doe"

    def test_billing_address_invalid_token(self, client, billing_mutation):
        variables = {
            "fullName": "John Doe",
            "contact": "1234567890",
            "address": "123 Test Street",
            "state": "Test State",
            "city": "Test City",
            "token": "invalid_token",
        }

        response = client.execute(billing_mutation, variables=variables)

        assert response is not None
        assert "data" in response
        assert "billingAddress" in response["data"]
        result = response["data"]["billingAddress"]

        assert result["status"] is False
        assert "invalid authentication token" in result["message"]

    def test_billing_address_missing_fields(self, client, billing_mutation):
        variables = {
            "fullName": "",
            "contact": "1234567890",
            "address": "123 Test Street",
            "state": "Test State",
            "city": "Test City",
        }

        response = client.execute(billing_mutation, variables=variables)

        assert response is not None
        assert "data" in response
        assert "billingAddress" in response["data"]
        result = response["data"]["billingAddress"]

        assert result["status"] is False
        assert "required" in result["message"].lower()


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


# @pytest.mark.django_db
# def test_payment_initiate_success(client, valid_token):
#     mutation = """
#         mutation paymentLink($amount: Float!, $token: String!, $description: String!, $redirectUrl: String!, $currency: String, $gateway: String!) {
#             paymentLink(amount: $amount, token: $token, description: $description, redirectUrl: $redirectUrl, currency: $currency, gateway: $gateway) {
#                 status
#                 message
#                 payment {
#                     id
#                     amount
#                     description
#                 }
#                 paymentLink
#             }
#         }
#     """
#     variables = {
#         "amount": 100.0,
#         "token": valid_token,
#         "description": "Test Payment",
#         "redirectUrl": "https://example.com/redirect",
#         "currency": "NGN",
#         "gateway": "paystack",
#     }
#     response = client.execute(mutation, variables=variables)

#     assert response["data"]["paymentLink"]["status"] is True
#     assert response["data"]["paymentLink"]["payment"]["amount"] == 100.0
#     assert (
#         response["data"]["paymentLink"]["payment"]["description"] == "Test Payment"
#     )


# @pytest.mark.django_db
# def test_payment_verification_success(
#     client, valid_token, user, valid_payment_ref, valid_transaction_id
# ):
#     # Create payment record
#     payment = Payment.objects.create(
#         amount=100.0,
#         user_id=str(user.id),
#         email=user.email,
#         name=user.full_name,
#         phone=user.phone_number,
#         description="Test Payment",
#         gateway="flutterwave",
#         ref=valid_payment_ref,
#         verified=False,
#         currency="USD",
#     )

#     mutation = """
#         mutation verifyPayment($transactionRef: String!, $transactionId: String!) {
#             verifyPayment(transactionRef: $transactionRef, transactionId: $transactionId) {
#                 status
#                 message
#                 transactionInfo
#             }
#         }
#     """

#     variables = {
#         "transactionRef": valid_payment_ref,
#         "transactionId": valid_transaction_id,
#     }

#     # Mock the verification response
#     mock_verification_response = {
#         "status": True,
#         "message": "Payment verified successfully",
#         "transaction_info": {
#             "amount": "100.0",
#             "currency": "USD",
#             "status": "successful",
#         },
#     }

#     with patch("bill.payment.verify_transaction") as mock_verify:
#         mock_verify.return_value = mock_verification_response

#         # Execute the mutation
#         response = client.execute(mutation, variables=variables)
#         print(response)

#         # Assert the GraphQL response structure
#         assert "errors" not in response
#         assert "data" in response
#         assert response["data"]["verifyPayment"]["status"] is True
#         assert (
#             response["data"]["verifyPayment"]["message"]
#             == "Payment verified successfully"
#         )
#         assert (
#             response["data"]["verifyPayment"]["transactionInfo"]
#             == mock_verification_response["transaction_info"]
#         )

#         # Verify the payment was updated in the database
#         payment.refresh_from_db()
#         assert payment.verified is True

#         # Verify the mock was called correctly
#         mock_verify.assert_called_once_with(valid_payment_ref, valid_transaction_id)
