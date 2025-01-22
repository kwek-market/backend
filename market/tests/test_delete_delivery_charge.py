import pytest
from graphene.test import Client
from market.mutation import DeleteDeliveryCharge  
from users.schema import schema
import time
import jwt
from django.contrib.auth import get_user_model
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
    return "valid_state_fee_id"


@pytest.mark.django_db
def test_delete_delivery_charge_success(client, valid_token, state_fee_id):
    mutation = """
        mutation {
            deleteDeliveryCharge(token: "valid_admin_token", id: "valid_state_fee_id") {
                status
                message
            }
        }
    """
    response = client.execute(mutation)
    print("This is the response", response)
    assert response["data"]["deleteDeliveryCharge"]["status"] == True
    assert (
        response["data"]["deleteDeliveryCharge"]["message"] == "successfully deleted!"
    )


@pytest.mark.django_db
def test_delete_delivery_charge_invalid_token(client, invalid_token, state_fee_id):
    mutation = """
        mutation {
            deleteDeliveryCharge(token: "invalid_admin_token", id: "valid_state_fee_id") {
                status
                message
            }
        }
    """
    response = client.execute(mutation)
    print("This is the response", response)
    assert response["data"]["deleteDeliveryCharge"]["status"] == False
    assert (
        response["data"]["deleteDeliveryCharge"]["message"] == "Authentication failed"
    )


@pytest.mark.django_db
def test_delete_delivery_charge_non_existing_id(client, valid_token):
    mutation = """
        mutation {
            deleteDeliveryCharge(token: "valid_admin_token", id: "non-existing-id") {
                status
                message
            }
        }
    """
    response = client.execute(mutation)
    print("This is the response", response)
    assert response["data"]["deleteDeliveryCharge"]["status"] == False
    assert (
        response["data"]["deleteDeliveryCharge"]["message"]
        == "state delivery doesn't exist"
    )
