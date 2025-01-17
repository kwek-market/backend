import jwt
import pytest
from django.conf import settings
from graphene.test import Client

from users.models import ExtendUser
from users.schema import schema


@pytest.mark.django_db
def test_change_password_success():
    user = ExtendUser.objects.create_user(
        email="test@example.com", password="old_password", username="test@example.com"
    )
    token = jwt.encode(
        {"user": user.email, "validity": True}, settings.SECRET_KEY, algorithm="HS256"
    ).decode(
        "utf-8"
    )  

    client = Client(schema)  # Initialize Graphene test client with your schema

    mutation = """
    mutation ChangePassword($token: String!, $password1: String!, $password2: String!) {
        changePassword(token: $token, password1: $password1, password2: $password2) {
            status
            message
        }
    }
    """
    variables = {
        "token": token,
        "password1": "new_password1",
        "password2": "new_password1",
    }

    response = client.execute(mutation, variables=variables)
    assert response["data"]["changePassword"]["status"] is True
    assert "Password Change Successful" in response["data"]["changePassword"]["message"]

    user.refresh_from_db()
    assert user.check_password("new_password1")


@pytest.mark.django_db
def test_user_password_update_success(client, user):
    mutation = """
    mutation UserPasswordUpdate($token: String!, $currentPassword: String!, $newPassword: String!) {
        userPasswordUpdate(token: $token, currentPassword: $currentPassword, newPassword: $newPassword) {
            status
            message
        }
    }
    """
    token = "valid_token"
    variables = {
        "token": token,
        "currentPassword": "old_password",
        "newPassword": "new_secure_password",
    }

    with patch("users.utils.validate_user_passwords") as mock_validate, patch(
        "users.models.ExtendUser.objects.get"
    ) as mock_user, patch("users.utils.check_password") as mock_check_password:

        mock_validate.return_value = True
        mock_user.return_value = user
        mock_check_password.return_value = True

        response = client.execute(mutation, variables=variables)
        data = response["data"]["userPasswordUpdate"]

        assert data["status"] is True
        assert data["message"] == "Password Change Successful"


@pytest.mark.django_db
def test_user_password_update_invalid_token(client):
    mutation = """
    mutation UserPasswordUpdate($token: String!, $currentPassword: String!, $newPassword: String!) {
        userPasswordUpdate(token: $token, currentPassword: $currentPassword, newPassword: $newPassword) {
            status
            message
        }
    }
    """
    variables = {
        "token": "invalid_token",
        "currentPassword": "old_password",
        "newPassword": "new_secure_password",
    }

    response = client.execute(mutation, variables=variables)
    data = response["data"]["userPasswordUpdate"]

    assert data["status"] is False
    assert "Invalid token" in data["message"]
