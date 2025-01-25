import pytest
from unittest.mock import patch


@pytest.mark.django_db
def test_revoke_token_success(client):
    mutation = """
    mutation RevokeToken($token: String!) {
        revokeToken(token: $token) {
            status
            message
            token
            payload
        }
    }
    """
    variables = {"token": "sample_token"}

    with patch("users.schema.expire_token") as mock_expire_token:
        mock_expire_token.return_value = {
            "status": True,
            "message": "Token revoked successfully",
            "token": "sample_token",
            "payload": "sample_payload",
        }

        response = client.execute(mutation, variables=variables)
        data = response["data"]["revokeToken"]

        assert data["status"] is True
        assert data["message"] == "Token revoked successfully"
        assert data["token"] == "sample_token"
        assert data["payload"] == "sample_payload"
