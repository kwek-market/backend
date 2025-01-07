import pytest
from unittest.mock import patch


@pytest.mark.django_db
def test_refresh_token_success(client):
    mutation = """
    mutation RefreshToken($token: String!, $email: String!) {
        refreshToken(token: $token, email: $email) {
            status
            message
            token
        }
    }
    """
    variables = {"token": "expired_token", "email": "test@example.com"}

    with patch("users.schema.refresh_user_token") as mock_refresh_token:
        mock_refresh_token.return_value = {
            "status": True,
            "message": "Token refreshed successfully",
            "token": "new_token",
        }

        response = client.execute(mutation, variables=variables)
        data = response["data"]["refreshToken"]

        assert data["status"] is True
        assert data["message"] == "Token refreshed successfully"
        assert data["token"] == "new_token"
