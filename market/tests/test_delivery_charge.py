# import pytest


# @pytest.mark.django_db
# def test_delete_delivery_charge_success(client, valid_token, state_fee_id):
#     mutation = """
#         mutation {
#             deleteDeliveryCharge(token: "%s", id: "%s") {
#                 status
#                 message
#             }
#         }
#     """ % (
#         valid_token,
#         state_fee_id,
#     )

#     response = client.execute(mutation)
#     print("This is the response", response)
#     assert response["data"]["deleteDeliveryCharge"]["status"] is True
#     assert (
#         response["data"]["deleteDeliveryCharge"]["message"] == "successfully deleted!"
#     )


# @pytest.mark.django_db
# def test_delete_delivery_charge_invalid_token(client, invalid_token, state_fee_id):
#     mutation = """
#         mutation {
#             deleteDeliveryCharge(token: "%s", id: "%s") {
#                 status
#                 message
#             }
#         }
#     """ % (
#         invalid_token,
#         state_fee_id,
#     )

#     response = client.execute(mutation)
#     print("This is the response", response)
#     assert response["data"]["deleteDeliveryCharge"]["status"] is False
#     assert (
#         response["data"]["deleteDeliveryCharge"]["message"] == "Authentication failed"
#     )


# @pytest.mark.django_db
# def test_delete_delivery_charge_non_existing_id(client, valid_token):
#     mutation = (
#         """
#         mutation {
#             deleteDeliveryCharge(token: "%s", id: "non-existing-id") {
#                 status
#                 message
#             }
#         }
#     """
#         % valid_token
#     )

#     response = client.execute(mutation)
#     print("This is the response", response)
#     assert response["data"]["deleteDeliveryCharge"]["status"] is False
#     assert (
#         response["data"]["deleteDeliveryCharge"]["message"]
#         == "state delivery doesn't exist"
#     )


# @pytest.mark.django_db
# def test_create_state_delivery_charge_success(client, valid_token):
#     mutation = """
#         mutation CreateStateDeliveryCharge($token: String!, $state: String!, $city: String!, $fee: Float!) {
#             createStateDeliveryCharge(token: $token, state: $state, city: $city, fee: $fee) {
#                 status
#                 message
#                 deliveryCharge {
#                     state
#                     city
#                     fee
#                 }
#             }
#         }
#     """
#     variables = {"token": valid_token, "state": "Lagos", "city": "Ikeja", "fee": 500.0}
#     response = client.execute(mutation, variables=variables)
#     assert response["data"]["createStateDeliveryCharge"]["status"] is True
#     assert (
#         response["data"]["createStateDeliveryCharge"]["message"]
#         == "successfully created!"
#     )


# @pytest.mark.django_db
# def test_create_state_delivery_charge_invalid_token(client, invalid_token):
#     mutation = """
#         mutation CreateStateDeliveryCharge($token: String!, $state: String!, $city: String!, $fee: Float!) {
#             createStateDeliveryCharge(token: $token, state: $state, city: $city, fee: $fee) {
#                 status
#                 message
#             }
#         }
#     """
#     variables = {
#         "token": invalid_token,
#         "state": "Lagos",
#         "city": "Ikeja",
#         "fee": 500.0,
#     }
#     response = client.execute(mutation, variables=variables)
#     assert response["data"]["createStateDeliveryCharge"]["status"] is False
#     assert (
#         response["data"]["createStateDeliveryCharge"]["message"]
#         == "Authentication failed"
#     )


# @pytest.mark.django_db
# def test_create_state_delivery_charge_invalid_state(client, valid_token):
#     mutation = """
#         mutation CreateStateDeliveryCharge($token: String!, $state: String!, $city: String!, $fee: Float!) {
#             createStateDeliveryCharge(token: $token, state: $state, city: $city, fee: $fee) {
#                 status
#                 message
#             }
#         }
#     """
#     variables = {
#         "token": valid_token,
#         "state": "InvalidState",
#         "city": "Ikeja",
#         "fee": 500.0,
#     }
#     response = client.execute(mutation, variables=variables)
#     assert response["data"]["createStateDeliveryCharge"]["status"] is False
#     assert (
#         response["data"]["createStateDeliveryCharge"]["message"]
#         == "Cannot find state..Please check that you entered the correct state!!"
#     )


# @pytest.mark.django_db
# def test_create_state_delivery_charge_city_exists(client, valid_token):
#     mutation = """
#         mutation CreateStateDeliveryCharge($token: String!, $state: String!, $city: String!, $fee: Float!) {
#             createStateDeliveryCharge(token: $token, state: $state, city: $city, fee: $fee) {
#                 status
#                 message
#             }
#         }
#     """
#     variables = {"token": valid_token, "state": "Lagos", "city": "Ikeja", "fee": 500.0}
#     response = client.execute(mutation, variables=variables)
#     assert response["data"]["createStateDeliveryCharge"]["status"] is False
#     assert (
#         response["data"]["createStateDeliveryCharge"]["message"]
#         == "city already exists for state"
#     )
