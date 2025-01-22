# import pytest
# from django.contrib.auth import get_user_model
# from django.test import Client
# from graphene.test import Client
# from graphql_jwt.testcases import JSONWebTokenTestCase

# from market.models import Cart, Wishlist
# from notifications.models import Notification
# from users.schema import schema


# @pytest.fixture
# def client():
#     return Client(schema)


# @pytest.fixture
# def user_data():
#     return {
#         "email": "testuser@example.com",
#         "full_name": "Test User",
#         "password1": "TestPassword123!",
#         "password2": "TestPassword123!",
#         "username": "testuser",
#     }


# @pytest.mark.django_db
# class TestUserFlow:
#     def test_create_user(self, client, user_data):
#         mutation = """
#         mutation CreateUser($email: String!, $full_name: String!, $password1: String!, $password2: String!) {
#             createUser(email: $email, fullName: $full_name, password1: $password1, password2: $password2) {
#                 status
#                 message
#             }
#         }
#         """
#         response = client.execute(mutation, variables=user_data)
#         assert response["data"]["createUser"]["status"] is True
#         assert (
#             "Successfully created account for"
#             in response["data"]["createUser"]["message"]
#         )

#         user = get_user_model().objects.get(email=user_data["email"])
#         assert user is not None
#         assert not user.is_verified
#         assert Cart.objects.filter(user=user).exists()
#         assert Wishlist.objects.filter(user=user).exists()
#         assert Notification.objects.filter(user=user).exists()

#     # def test_resend_verification_email(self, client, user_data):
#     #     user = get_user_model().objects.create_user(
#     #         email=user_data["email"],
#     #         username=user_data["username"],
#     #         full_name=user_data["full_name"],
#     #         password=user_data["password1"],
#     #     )
#     #     mutation = """
#     #     mutation ResendVerification($email: String!) {
#     #         resendVerification(email: $email) {
#     #             status
#     #             message
#     #         }
#     #     }
#     #     """
#     #     variables = {"email": user_data["email"]}
#     #     response = client.execute(mutation, variables=variables)

#     #     assert response["data"]["resendVerification"]["status"] is True
#     #     assert (
#     #         "Successfully sent email to"
#     #         in response["data"]["resendVerification"]["message"]
#     #     )

#     # def test_verify_email(self, client, user_data):
#     #     user = get_user_model().objects.create_user(
#     #         email=user_data["email"],
#     #         username=user_data["username"],
#     #         full_name=user_data["full_name"],
#     #         password=user_data["password1"],
#     #         is_verified=False,
#     #     )
#     #     mutation = """
#     #     mutation VerifyEmail($email: String!) {
#     #         verifyEmail(email: $email) {
#     #             status
#     #             message
#     #         }
#     #     }
#     #     """
#     #     variables = {"email": user_data["email"], "username": user_data["email"]}
#     #     response = client.execute(mutation, variables=variables)
        
#     #     print(response)  # Debugging

#     #     assert "data" in response
#     #     assert response["data"]["verifyEmail"]["status"] is True
#     #     assert (
#     #         "Email verified successfully" in response["data"]["verifyEmail"]["message"]
#     #     )

#     #     user.refresh_from_db()
#     #     assert user.is_verified

#     def test_login_user(self, client, user_data):
#         user = get_user_model().objects.create_user(
#             email=user_data["email"],
#             username=user_data["username"],
#             full_name=user_data["full_name"],
#             password=user_data["password1"],
#             is_verified=True,
#         )
#         mutation = """ 
#         mutation LoginUser($email: String!, $password: String!, $ip: String!) {
#             loginUser(email: $email, password: $password, ip: $ip) {
#                 status
#                 token
#                 message
#             }
#         }
#         """
#         variables = {
#             "email": user_data["email"],
#             "password": user_data["password1"],
#             "ip": "192.168.0.1",
#         }
#         response = client.execute(mutation, variables=variables)

#         assert response["data"]["loginUser"]["status"] is True
#         assert "You logged in successfully." in response["data"]["loginUser"]["message"]
#         assert "token" in response["data"]["loginUser"]

#     def test_login_user_with_unverified_email(self, client, user_data):
#         user = get_user_model().objects.create_user(
#             email=user_data["email"],
#             username=user_data["username"],
#             full_name=user_data["full_name"],
#             password=user_data["password1"],
#             is_verified=False,
#         )
#         mutation = """
#         mutation LoginUser($email: String!, $password: String!, $ip: String!) {
#             loginUser(email: $email, password: $password, ip: $ip) {
#                 status
#                 message
#             }
#         }
#         """
#         variables = {
#             "email": user_data["email"],
#             "password": user_data["password1"],
#             "ip": "192.168.0.1",
#         }
#         response = client.execute(mutation, variables=variables)

#         assert response["data"]["loginUser"]["status"] is False
#         assert "Your email is not verified" in response["data"]["loginUser"]["message"]
