# import time

# import jwt
# import pytest
# from graphene.test import Client
# from django.conf import   settings
# from market.mutation import CreateStateDeliveryCharge, UpdateStateDeliveryCharge
# from users.models import ExtendUser
# from users.schema import schema


# @pytest.fixture
# def valid_token():
#     """
#     Generates a valid admin token for testing.
#     """
#     # Create or fetch a valid admin user
#     admin_user = ExtendUser.objects.create(
#         email="admin@example.com",
#         is_admin=True,
#         is_verified=True,
#         password="password123",
#     )

#     current_time = int(time.time())
#     payload = {
#         "username": admin_user.email,
#         "exp": current_time + 3600,  # Token valid for 1 hour
#         "origIat": current_time,
#     }
#     token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
#     return token


# @pytest.fixture
# def invalid_token():
#     """
#     Generates an invalid token for testing.
#     """
#     current_time = int(time.time())
#     payload = {
#         "username": "fake_user@example.com",
#         "exp": current_time + 3600,
#         "origIat": current_time,
#     }
#     # Use a different secret key to make the token invalid
#     invalid_secret_key = "invalid_secret_key"
#     token = jwt.encode(payload, invalid_secret_key, algorithm="HS256")
#     return token


# @pytest.fixture
# def client():
#     return Client(schema)


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
#     assert response["data"]["createStateDeliveryCharge"]["status"] == True
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
#     assert response["data"]["createStateDeliveryCharge"]["status"] == False
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
#     assert response["data"]["createStateDeliveryCharge"]["status"] == False
#     assert (
#         response["data"]["createStateDeliveryCharge"]["message"]
#         == "Cannot find state..Please check that you entered the correct state!!"
#     )


# @pytest.mark.django_db
# def test_create_state_delivery_charge_city_exists(client, valid_token):
#     # Assume "Ikeja" already exists for "Lagos" in the database
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
#     assert response["data"]["createStateDeliveryCharge"]["status"] == False
#     assert (
#         response["data"]["createStateDeliveryCharge"]["message"]
#         == "city already exists for state"
#     )
