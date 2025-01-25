import pytest
from unittest.mock import patch


@pytest.mark.django_db
def test_send_password_reset_email_success(client):
    mutation = """
    mutation SendPasswordResetEmail($email: String!) {
        sendPasswordResetEmail(email: $email) {
            status
            message
        }
    }
    """
    variables = {"email": "test@example.com"}

    with patch("users.sendmail.send_password_reset_email") as mock_send_email:
        mock_send_email.return_value = {"status": True}

        response = client.execute(mutation, variables=variables)
        data = response["data"]["sendPasswordResetEmail"]

        assert data["status"] is True
        assert "Successfully sent password reset link" in data["message"]
