# import jwt
# import pytest
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from graphene.test import Client

# from users.schema import schema

# User = get_user_model()


# @pytest.fixture
# def client():
#     return Client(schema)


# @pytest.mark.django_db
# def test_user_password_update_success(client):
#     user = User.objects.create_user(
#         email="test@example.com",
#         password="current_password",
#         username="test@example.com",
#     )
#     token = jwt.encode({"username": user.email}, settings.SECRET_KEY, algorithm="HS256")

#     mutation = """
#     mutation UserPasswordUpdate($token: String!, $currentPassword: String!, $newPassword: String!) {
#         userPasswordUpdate(token: $token, currentPassword: $currentPassword, newPassword: $newPassword) {
#             status
#             message
#         }
#     }
#     """
#     variables = {
#         "token": token,
#         "currentPassword": "current_password",
#         "newPassword": "new_secure_password",
#     }

#     response = client.execute(mutation, variables=variables)
#     data = response["data"]["userPasswordUpdate"]

#     user.refresh_from_db()
#     assert data["status"] is True
#     assert user.check_password("new_secure_password")
