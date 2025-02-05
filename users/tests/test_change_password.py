# import time
# from unittest.mock import patch

# import jwt
# import pytest
# from django.conf import settings
# from graphene.test import Client

# from users.models import ExtendUser
# from users.schema import schema


# # Fixture for the Graphene test client
# @pytest.fixture
# def client():
#     return Client(schema)


# # Fixture for creating a user
# @pytest.fixture
# def user():
#     return ExtendUser.objects.create_user(
#         email="test@example.com", password="old_password123A#", username="test@example.com"
#     )


# @pytest.mark.django_db
# def test_change_password_success(client, user):
#     # Generate a valid JWT token
#     ct = int(time.time())
#     payload = {
#         "email": user.email,
#         "exp": ct + 151200,  # Token expiration time (e.g., 42 hours)
#         "origIat": ct,
#     }
#     token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

#     mutation = """
#     mutation ChangePassword($token: String!, $password1: String!, $password2: String!) {
#         changePassword(token: $token, password1: $password1, password2: $password2) {
#             status
#             message
#         }
#     }
#     """
#     variables = {
#         "token": token,
#         "password1": "new_password123A#",
#         "password2": "new_password123A#",
#     }

#     response = client.execute(mutation, variables=variables)
#     #assert response["data"]["changePassword"]["status"] is True
#     assert "Password Change Successful" in response["data"]["changePassword"]["message"]

#     user.refresh_from_db()
#     assert user.check_password("new_password1")


# @pytest.mark.django_db
# def test_user_password_update_success(client, user):
#     mutation = """
#     mutation UserPasswordUpdate($token: String!, $currentPassword: String!, $newPassword: String!) {
#         userPasswordUpdate(token: $token, currentPassword: $currentPassword, newPassword: $newPassword) {
#             status
#             message
#         }
#     }
#     """
#     token = "valid_token"
#     variables = {
#         "token": token,
#         "currentPassword": "old_password",
#         "newPassword": "new_secure_password",
#     }

#     with patch("users.validate.validate_user_passwords") as mock_validate, patch(
#         "users.models.ExtendUser.objects.get"
#     ) as mock_user, patch(
#         "users.validate.validate_user_passwords"
#     ) as mock_check_password:

#         mock_validate.return_value = True
#         mock_user.return_value = user
#         mock_check_password.return_value = True

#         response = client.execute(mutation, variables=variables)
#         data = response["data"]["userPasswordUpdate"]

#         assert data["status"] is True
#         assert data["message"] == "Password Change Successful"


# @pytest.mark.django_db
# def test_user_password_update_invalid_token(client):
#     mutation = """
#     mutation UserPasswordUpdate($token: String!, $currentPassword: String!, $newPassword: String!) {
#         userPasswordUpdate(token: $token, currentPassword: $currentPassword, newPassword: $newPassword) {
#             status
#             message
#         }
#     }
#     """
#     variables = {
#         "token": "invalid_token",
#         "currentPassword": "old_password",
#         "newPassword": "new_secure_password",
#     }

#     response = client.execute(mutation, variables=variables)
#     data = response["data"]["userPasswordUpdate"]

#     assert data["status"] is False
#     assert "Invalid token" in data["message"]
