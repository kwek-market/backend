import pytest
from unittest.mock import patch
from graphene.test import Client
from users.schema import schema  


@pytest.mark.django_db
def test_send_password_reset_email_success():
    mutation = """
    mutation SendPasswordResetEmail($email: String!) {
        sendPasswordResetEmail(email: $email) {
            status
            message
        }
    }
    """
    variables = {"email": "test@example.com"}


    client = Client(schema)

    with patch("users.sendmail.send_password_reset_email") as mock_send_email:
        # Mock the email sending function
        mock_send_email.return_value = {"status": True}

        # Execute the mutation
        response = client.execute(mutation, variables=variables)
        data = response["data"]["sendPasswordResetEmail"]

        # Assert the response
        assert data["status"] is True
        assert "Successfully sent password reset link" in data["message"]
