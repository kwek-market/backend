import pytest
from graphene.test import Client
from mutations import (
    CreateStateDeliveryCharge,
    UpdateStateDeliveryCharge,
)  # Assuming mutations are in this path
from project.schema import schema


@pytest.fixture
def valid_token():
    # Provide a valid admin token here
    return "valid_admin_token"


@pytest.fixture
def invalid_token():
    # Provide an invalid or non-admin token
    return "invalid_admin_token"


@pytest.fixture
def client():
    return Client(schema)


def test_create_state_delivery_charge_success(client, valid_token):
    mutation = """
        mutation {
            createStateDeliveryCharge(token: "valid_admin_token", state: "Lagos", city: "Ikeja", fee: 500.0) {
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
    assert response["data"]["createStateDeliveryCharge"]["status"] == True
    assert (
        response["data"]["createStateDeliveryCharge"]["message"]
        == "successfully created!"
    )


def test_create_state_delivery_charge_invalid_token(client, invalid_token):
    mutation = """
        mutation {
            createStateDeliveryCharge(token: "invalid_admin_token", state: "Lagos", city: "Ikeja", fee: 500.0) {
                status
                message
            }
        }
    """
    response = client.execute(mutation)
    assert response["data"]["createStateDeliveryCharge"]["status"] == False
    assert (
        response["data"]["createStateDeliveryCharge"]["message"]
        == "Authentication failed"
    )


def test_create_state_delivery_charge_invalid_state(client, valid_token):
    mutation = """
        mutation {
            createStateDeliveryCharge(token: "valid_admin_token", state: "InvalidState", city: "Ikeja", fee: 500.0) {
                status
                message
            }
        }
    """
    response = client.execute(mutation)
    assert response["data"]["createStateDeliveryCharge"]["status"] == False
    assert (
        response["data"]["createStateDeliveryCharge"]["message"]
        == "Cannot find state..Please check that you entered the correct state!!"
    )


def test_create_state_delivery_charge_city_exists(client, valid_token):
    # Assume "Ikeja" already exists for "Lagos" in database
    mutation = """
        mutation {
            createStateDeliveryCharge(token: "valid_admin_token", state: "Lagos", city: "Ikeja", fee: 500.0) {
                status
                message
            }
        }
    """
    response = client.execute(mutation)
    assert response["data"]["createStateDeliveryCharge"]["status"] == False
    assert (
        response["data"]["createStateDeliveryCharge"]["message"]
        == "city already exists for state"
    )

