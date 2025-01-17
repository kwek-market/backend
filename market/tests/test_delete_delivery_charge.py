import pytest
from graphene.test import Client
from market.mutation import DeleteDeliveryCharge  
from users.schema import schema


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
    return "valid_state_fee_id"


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
    assert response["data"]["deleteDeliveryCharge"]["status"] == True
    assert (
        response["data"]["deleteDeliveryCharge"]["message"] == "successfully deleted!"
    )


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
    assert response["data"]["deleteDeliveryCharge"]["status"] == False
    assert (
        response["data"]["deleteDeliveryCharge"]["message"] == "Authentication failed"
    )


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
    assert response["data"]["deleteDeliveryCharge"]["status"] == False
    assert (
        response["data"]["deleteDeliveryCharge"]["message"]
        == "state delivery doesn't exist"
    )
