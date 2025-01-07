import pytest
from users.models import ExtendUser
import jwt
from django.conf import settings


@pytest.mark.django_db
def test_change_password_success(client):
    user = ExtendUser.objects.create_user(
        email="test@example.com", password="old_password"
    )
    token = jwt.encode(
        {"user": user.email, "validity": True}, settings.SECRET_KEY, algorithm="HS256"
    )

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
        "password1": "new_password",
        "password2": "new_password",
    }

    response = client.execute(mutation, variables=variables)
    data = response["data"]["changePassword"]

    user.refresh_from_db()
    assert data["status"] is True
    assert user.check_password("new_password")
