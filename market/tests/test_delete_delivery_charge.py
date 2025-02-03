# import pytest


# @pytest.mark.django_db
# def test_delete_delivery_charge_success(client, valid_token, state_fee_id):
#     mutation = f"""
#         mutation {{
#             deleteDeliveryCharge(token: "{valid_token}", id: "{state_fee_id}") {{
#                 status
#                 message
#             }}
#         }}
#     """
#     response = client.execute(mutation)
#     print("This is the response", response)
#     assert response["data"]["deleteDeliveryCharge"]["status"] is True
#     assert (
#         response["data"]["deleteDeliveryCharge"]["message"] == "successfully deleted!"
#     )


# @pytest.mark.django_db
# def test_delete_delivery_charge_invalid_token(client, invalid_token, state_fee_id):
#     mutation = f"""
#         mutation {{
#             deleteDeliveryCharge(token: "{invalid_token}", id: "{state_fee_id}") {{
#                 status
#                 message
#             }}
#         }}
#     """
#     response = client.execute(mutation)
#     print("This is the response", response)
#     assert response["data"]["deleteDeliveryCharge"]["status"] is False
#     assert (
#         response["data"]["deleteDeliveryCharge"]["message"] == "Authentication failed"
#     )


# @pytest.mark.django_db
# def test_delete_delivery_charge_non_existing_id(client, valid_token):
#     mutation = f"""
#         mutation {{
#             deleteDeliveryCharge(token: "{valid_token}", id: "non-existing-id") {{
#                 status
#                 message
#             }}
#         }}
#     """
#     response = client.execute(mutation)
#     print("This is the response", response)
#     assert response["data"]["deleteDeliveryCharge"]["status"] is False
#     assert (
#         response["data"]["deleteDeliveryCharge"]["message"]
#         == "state delivery doesn't exist"
#     )
