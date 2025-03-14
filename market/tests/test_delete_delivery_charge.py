import pytest

import uuid
@pytest.mark.django_db
def test_delete_delivery_charge_success(client, admin_token, state_fee_id):
    mutation = f"""
        mutation {{
            deleteStateDeliveryFee(token: "{admin_token}", id: "{state_fee_id.id}" {{
                status
                message
            }}
        }}
    """
    response = client.execute(mutation)
    print("This is the response", response)
    assert response["data"]["deleteStateDeliveryFee"]["status"] is True
    assert (
        response["data"]["deleteStateDeliveryFee"]["message"] == "successfully deleted!"
    )


@pytest.mark.django_db
def test_delete_delivery_charge_invalid_token(client, invalid_token, state_fee_id):
    mutation = f"""
    mutation {{
        deleteStateDeliveryFee(token: "{admin_token}", id: "{state_fee_id.id}") {{
            status
            message
        }}
    }}
    """

    response = client.execute(mutation)
    print("This is the response", response)
    assert response["data"]["deleteStateDeliveryFee"]["status"] is False
    assert (
        response["data"]["deleteStateDeliveryFee"]["message"] == "Authentication failed"
    )


@pytest.mark.django_db
def test_delete_delivery_charge_non_existing_id(client, admin_token):
    mutation = (f"""
        mutation {{
            deleteStateDeliveryFee(token: "{admin_token}", id: "{uuid.uuid4()}") {{
                status
                message
            }}
        }}
    """
    )
    response = client.execute(mutation)
    assert response["data"]["deleteStateDeliveryFee"]["status"] is False
    assert (
        response["data"]["deleteStateDeliveryFee"]["message"]
        == "state delivery doesn't exist"
    )
