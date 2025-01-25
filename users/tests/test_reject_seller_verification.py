import pytest
from unittest.mock import patch
from graphene.test import Client
from users.schema import schema

@pytest.mark.django_db
def test_reject_seller_verification_success(client):
    mutation = """
    mutation RejectSellerVerification($email: String!) {
        rejectSellerVerification(email: $email) {
            status
            message
        }
    }
    """
    variables = {"email": "seller@example.com"}

    with patch("users.models.ExtendUser.objects.get") as mock_user, patch(
        "users.models.SellerProfile.objects.get"
    ) as mock_seller, patch(
        "users.models.Notification.objects.filter"
    ) as mock_notification_filter:

        mock_user.return_value = Mock(id=1, email="seller@example.com")
        mock_seller.return_value = Mock(
            seller_is_verified=True, seller_is_rejected=False
        )
        mock_notification_filter.return_value.exists.return_value = False

        response = client.execute(mutation, variables=variables)
        data = response["data"]["rejectSellerVerification"]

        assert data["status"] is True
        assert data["message"] == "Successful"


@pytest.mark.django_db
def test_reject_seller_verification_not_a_seller(client):
    mutation = """
    mutation RejectSellerVerification($email: String!) {
        rejectSellerVerification(email: $email) {
            status
            message
        }
    }
    """
    variables = {"email": "not_a_seller@example.com"}

    with patch("users.models.ExtendUser.objects.get") as mock_user, patch(
        "users.models.SellerProfile.objects.get",
        side_effect=Exception("user is not a seller"),
    ):

        mock_user.return_value = Mock(id=2, email="not_a_seller@example.com")

        response = client.execute(mutation, variables=variables)
        data = response["data"]["rejectSellerVerification"]

        assert data["status"] is False
        assert data["message"] == "user is not a seller"


@pytest.mark.django_db
def test_reject_seller_verification_error(client):
    mutation = """
    mutation RejectSellerVerification($email: String!) {
        rejectSellerVerification(email: $email) {
            status
            message
        }
    }
    """
    variables = {"email": "error@example.com"}

    with patch(
        "users.models.ExtendUser.objects.get", side_effect=Exception("Unexpected error")
    ):
        response = client.execute(mutation, variables=variables)
        data = response["data"]["rejectSellerVerification"]

        assert data["status"] is False
        assert "Unexpected error" in data["message"]
