import time
from unittest.mock import patch

import jwt
import pytest
from graphene.test import Client

from users.schema import schema
from django.conf import settings

@pytest.fixture
def client():
    return Client(schema)


@pytest.fixture
def user():
    return User.objects.create_user(
        email="test@example.com",
        password="password123",
        username="test@example.com",
    )


@pytest.fixture
def valid_token(user):
    payload = {
        "username": user.email,
        "exp": int(time.time()) + 3600,  # Token valid for 1 hour
        "origIat": int(time.time()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256").decode("utf-8")


# @pytest.mark.django_db
# def test_user_password_update_weak_password(client):
#     mutation = """
#     mutation UserPasswordUpdate($token: String!, $currentPassword: String!, $newPassword: String!) {
#         userPasswordUpdate(token: $token, currentPassword: $currentPassword, newPassword: $newPassword) {
#             status
#             message
#         }
#     }
#     """
#     variables = {
#         "token": valid_token,
#         "currentPassword": "old_password",
#         "newPassword": "123",
#     }

#     with patch("users.validate.validate_user_passwords") as mock_validate:
#         mock_validate.return_value = {"status": False, "message": "Weak password"}

#         response = client.execute(mutation, variables=variables)
#         data = response["data"]["userPasswordUpdate"]

#         assert data["status"] is False
#         assert data["message"] == "Weak password"


@pytest.mark.django_db
def test_start_selling_missing_field(client):
    mutation = """
    mutation StartSelling(
        $token: String!,
        $firstname: String!,
        $lastname: String!,
        $phoneNumber: String!,
        $shopName: String!,
        $shopUrl: String!,
        $shopAddress: String!,
        $state: String!,
        $lga: String!,
        $landmark: String!,
        $howYouHeardAboutUs: String!,
        $acceptedPolicy: Boolean!
    ) {
        startSelling(
            token: $token,
            firstname: $firstname,
            lastname: $lastname,
            phoneNumber: $phoneNumber,
            shopName: $shopName,
            shopUrl: $shopUrl,
            shopAddress: $shopAddress,
            state: $state,
            lga: $lga,
            landmark: $landmark,
            howYouHeardAboutUs: $howYouHeardAboutUs,
            acceptedPolicy: $acceptedPolicy
        ) {
            status
            message
        }
    }
    """
    variables = {
        "token": valid_token,
        "firstname": "John",
        "lastname": "Doe",
        "phoneNumber": "1234567890",
        "shopName": "Doe's Shop",
        # Missing `shopUrl`
        "shopAddress": "123 Market St",
        "state": "California",
        "lga": "Los Angeles",
        "landmark": "Near Central Park",
        "howYouHeardAboutUs": "Internet",
        "acceptedPolicy": True,
    }

    response = client.execute(mutation, variables=variables)
    assert "shopUrl" in str(response["errors"][0]["message"])
