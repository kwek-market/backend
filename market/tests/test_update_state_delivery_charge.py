# import pytest


# @pytest.mark.django_db
# def test_update_state_delivery_charge_success(client, valid_token, state_fee_id):
#     mutation = f"""
#         mutation {{
#             updateStateDeliveryCharge(token: "{valid_token}", id: "{state_fee_id}", state: "Lagos", city: "Ikeja", fee: 600.0) {{
#                 status
#                 message
#                 deliveryCharge {{
#                     state
#                     city
#                     fee
#                 }}
#             }}
#         }}
#     """
#     response = client.execute(mutation)
#     assert response["data"]["updateStateDeliveryCharge"]["status"] == True
#     assert (
#         response["data"]["updateStateDeliveryCharge"]["message"]
#         == "successfully updated!"
#     )


# @pytest.mark.django_db
# def test_update_state_delivery_charge_invalid_token(
#     client, invalid_token, state_fee_id
# ):
#     mutation = f"""
#         mutation {{
#             updateStateDeliveryCharge(token: "{invalid_token}", id: "{state_fee_id}", state: "Lagos", city: "Ikeja", fee: 600.0) {{
#                 status
#                 message
#             }}
#         }}
#     """
#     response = client.execute(mutation)
#     assert response["data"]["updateStateDeliveryCharge"]["status"] == False
#     assert (
#         response["data"]["updateStateDeliveryCharge"]["message"]
#         == "Authentication failed"
#     )
