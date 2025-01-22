import time

import jwt
import pytest
from django.contrib.auth import get_user_model
from graphene.test import Client

from market.mutation import UpdateStateDeliveryCharge
from users.schema import schema
from django.conf import settings
User = get_user_model()


@pytest.fixture
def valid_token():
    """
    Generates a valid admin token for testing.
    """
    # Create or fetch a valid admin user
    admin_user = User.objects.create(
        email="admin@example.com",
        is_admin=True,
        is_verified=True,
        password="password123",
    )

    current_time = int(time.time())
    payload = {
        "username": admin_user.email,
        "exp": current_time + 3600,  # Token valid for 1 hour
        "origIat": current_time,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


@pytest.fixture
def invalid_token():
    """
    Generates an invalid token for testing.
    """
    current_time = int(time.time())
    payload = {
        "username": "fake_user@example.com",
        "exp": current_time + 3600,
        "origIat": current_time,
    }
    # Use a different secret key to make the token invalid
    invalid_secret_key = "invalid_secret_key"
    token = jwt.encode(payload, invalid_secret_key, algorithm="HS256")
    return token


@pytest.fixture
def client():
    return Client(schema)


@pytest.fixture
def state_fee_id():
    # Return a valid state fee ID for testing purposes
    return "valid_state_fee_id"


@pytest.mark.django_db
def test_update_state_delivery_charge_success(client, valid_token, state_fee_id):
    mutation = """
        mutation {
            updateStateDeliveryCharge(token: "valid_admin_token", id: "valid_state_fee_id", state: "Lagos", city: "Ikeja", fee: 600.0) {
                status
                message
                deliveryCharge {
                    state
                    city
                    fee
                }
            }
        }
    """
    response = client.execute(mutation)
    assert response["data"]["updateStateDeliveryCharge"]["status"] == True
    assert (
        response["data"]["updateStateDeliveryCharge"]["message"]
        == "successfully updated!"
    )


@pytest.mark.django_db
def test_update_state_delivery_charge_invalid_token(
    client, invalid_token, state_fee_id
):
    mutation = """
        mutation {
            updateStateDeliveryCharge(token: "invalid_admin_token", id: "valid_state_fee_id", state: "Lagos", city: "Ikeja", fee: 600.0) {
                status
                message
            }
        }
    """
    response = client.execute(mutation)
    assert response["data"]["updateStateDeliveryCharge"]["status"] == False
    assert (
        response["data"]["updateStateDeliveryCharge"]["message"]
        == "Authentication failed"
    )


@pytest.mark.django_db
def test_update_state_delivery_charge_invalid_state(client, valid_token, state_fee_id):
    mutation = """
        mutation {
            updateStateDeliveryCharge(token: "valid_admin_token", id: "valid_state_fee_id", state: "InvalidState", city: "Ikeja", fee: 600.0) {
                status
                message
            }
        }
    """
    response = client.execute(mutation)
    assert response["data"]["updateStateDeliveryCharge"]["status"] == False
    assert (
        response["data"]["updateStateDeliveryCharge"]["message"]
        == "Cannot find state..Please check that you entered the correct state!!"
    )


@pytest.mark.django_db
def test_update_state_delivery_charge_non_existing_id(client, valid_token):
    mutation = """
        mutation {
            updateStateDeliveryCharge(token: "valid_admin_token", id: "non-existing-id", state: "Lagos", city: "Ikeja", fee: 600.0) {
                status
                message
            }
        }
    """
    response = client.execute(mutation)
    assert response["data"]["updateStateDeliveryCharge"]["status"] == False
    assert (
        response["data"]["updateStateDeliveryCharge"]["message"]
        == "Cannot find charge..Please create before updating"
    )
