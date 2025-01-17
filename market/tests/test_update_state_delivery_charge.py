import pytest
from graphene.test import Client
from users.schema import schema

from market.mutation import (
    UpdateStateDeliveryCharge,
)  # Assuming mutations are in this path


@pytest.fixture
def valid_token():
    return "valid_admin_token"


@pytest.fixture
def invalid_token():
    return "invalid_admin_token"


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
