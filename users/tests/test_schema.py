import time

import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from graphene.test import Client
from graphql_jwt.testcases import JSONWebTokenTestCase

from market.models import Cart, Wishlist
from notifications.models import Notification
from users.schema import schema

User = get_user_model()

@pytest.fixture
def client():
    return Client(schema)


@pytest.fixture
def user_data():
    return {
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password1": "TestPassword123!",
        "password2": "TestPassword123!",
        "username": "testuser",
    }


@pytest.mark.django_db
class TestUserFlow:

    def test_create_user(self, client, user_data):
        mutation = """
        mutation CreateUser($email: String!, $fullName: String!, $password1: String!, $password2: String!) {
            createUser(email: $email, fullName: $fullName, password1: $password1, password2: $password2) {
                status
                message
            }
        }
        """
        response = client.execute(
            mutation,
            variables={
                "email": user_data["email"],
                "fullName": user_data["full_name"],
                "password1": user_data["password1"],
                "password2": user_data["password2"],
            },
        )

        assert response.get("data", {}).get("createUser") is not None
        create_user_result = response["data"]["createUser"]
        assert create_user_result["status"] is True
        assert "Successfully created account for" in create_user_result["message"]

        user = get_user_model().objects.get(email=user_data["email"])
        assert user is not None
        assert not user.is_verified
        assert Cart.objects.filter(user=user).exists()
        assert Wishlist.objects.filter(user=user).exists()
        assert Notification.objects.filter(user=user).exists()

    # def test_verify_email(self, client, user_data):
    #     # Create unverified user
    #     user = get_user_model().objects.create_user(
    #         email=user_data["email"],
    #         username=user_data["email"],  # Use email as username
    #         full_name=user_data["full_name"],
    #         password=user_data["password1"],
    #         is_verified=False,
    #     )

    #     # Create verification token
    #     ct = int(time.time())
    #     payload = {
    #         User.USERNAME_FIELD: user_data["email"],
    #         "exp": ct + 151200,
    #         "origIat": ct,
    #     }
    #     token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    #     mutation = """
    #     mutation VerifyUser($token: String!) {
    #         verifyUser(token: $token) {
    #             status
    #             message
    #         }
    #     }
    #     """
    #     response = client.execute(mutation, variables={"token": token})

    #     assert response.get("data", {}).get("verifyUser") is not None
    #     verify_result = response["data"]["verifyUser"]
    #     assert verify_result["status"] is True
    #     assert "Email verified successfully" in verify_result["message"]

    #     user.refresh_from_db()
    #     assert user.is_verified

    # def test_resend_verification_email(self, client, user_data):
    #     # Create unverified user
    #     user = get_user_model().objects.create_user(
    #         email=user_data["email"],
    #         username=user_data["email"],
    #         full_name=user_data["full_name"],
    #         password=user_data["password1"],
    #         is_verified=False,
    #     )

    #     mutation = """
    #     mutation ResendVerification($email: String!) {
    #         resendVerification(email: $email) {
    #             status
    #             message
    #         }
    #     }
    #     """
    #     response = client.execute(mutation, variables={"email": user_data["email"]})

    #     assert response.get("data", {}).get("resendVerification") is not None
    #     resend_result = response["data"]["resendVerification"]
    #     assert resend_result["status"] is True
    #     assert "Verification email sent successfully" in resend_result["message"]

    def test_login_user(self, client, user_data):
        user = get_user_model().objects.create_user(
            email=user_data["email"],
            username=user_data["username"],
            full_name=user_data["full_name"],
            password=user_data["password1"],
            is_verified=True,
        )
        mutation = """ 
        mutation LoginUser($email: String!, $password: String!, $ip: String!) {
            loginUser(email: $email, password: $password, ip: $ip) {
                status
                token
                message
            }
        }
        """
        variables = {
            "email": user_data["email"],
            "password": user_data["password1"],
            "ip": "192.168.0.1",
        }
        response = client.execute(mutation, variables=variables)

        assert response["data"]["loginUser"]["status"] is True
        assert "You logged in successfully." in response["data"]["loginUser"]["message"]
        assert "token" in response["data"]["loginUser"]

    def test_login_user_with_unverified_email(self, client, user_data):
        user = get_user_model().objects.create_user(
            email=user_data["email"],
            username=user_data["username"],
            full_name=user_data["full_name"],
            password=user_data["password1"],
            is_verified=False,
        )
        mutation = """
        mutation LoginUser($email: String!, $password: String!, $ip: String!) {
            loginUser(email: $email, password: $password, ip: $ip) {
                status
                message
            }
        }
        """
        variables = {
            "email": user_data["email"],
            "password": user_data["password1"],
            "ip": "192.168.0.1",
        }
        response = client.execute(mutation, variables=variables)

        assert response["data"]["loginUser"]["status"] is False
        assert "Your email is not verified" in response["data"]["loginUser"]["message"]
