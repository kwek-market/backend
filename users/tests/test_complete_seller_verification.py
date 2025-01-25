import pytest
from unittest.mock import patch
from graphene.test import Client
from users.schema import schema


@pytest.mark.django_db
def test_complete_seller_verification_success(client):
    mutation = """
    mutation CompleteSellerVerification($email: String!) {
        completeSellerVerification(email: $email) {
            status
            message
        }
    }
    """
    variables = {"email": "seller@example.com"}

    with patch("users.models.ExtendUser.objects.get") as mock_user, patch(
        "users.models.SellerProfile.objects.get"
    ) as mock_seller, patch(
        "users.models.StoreDetail.objects.filter"
    ) as mock_store_filter, patch(
        "users.models.Wallet.objects.filter"
    ) as mock_wallet_filter, patch(
        "users.models.Notification.objects.filter"
    ) as mock_notification_filter, patch(
        "users.utils.push_to_client"
    ), patch(
        "users.utils.SendEmailNotification"
    ):

        mock_user.return_value = Mock(id=1, email="seller@example.com")
        mock_seller.return_value = Mock(
            seller_is_verified=False,
            seller_is_rejected=False,
            shop_name="Test Shop",
            shop_address="123 Test Street",
        )
        mock_store_filter.return_value.exists.return_value = False
        mock_wallet_filter.return_value.exists.return_value = False
        mock_notification_filter.return_value.exists.return_value = False

        response = client.execute(mutation, variables=variables)
        data = response["data"]["completeSellerVerification"]

        assert data["status"] is True
        assert data["message"] == "Successful"


@pytest.mark.django_db
def test_complete_seller_verification_not_a_seller(client):
    mutation = """
    mutation CompleteSellerVerification($email: String!) {
        completeSellerVerification(email: $email) {
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
        data = response["data"]["completeSellerVerification"]

        assert data["status"] is False
        assert data["message"] == "user is not a seller"


@pytest.mark.django_db
def test_complete_seller_verification_error(client):
    mutation = """
    mutation CompleteSellerVerification($email: String!) {
        completeSellerVerification(email: $email) {
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
        data = response["data"]["completeSellerVerification"]

        assert data["status"] is False
        assert "Unexpected error" in data["message"]


@pytest.mark.django_db
def test_complete_seller_verification_permission_denied(client):
    mutation = """
    mutation CompleteSellerVerification($email: String!) {
        completeSellerVerification(email: $email) {
            status
            message
        }
    }
    """
    variables = {"email": "seller@example.com"}
    user = UserFactory(is_staff=False)  # Create a non-admin user

    client.force_login(user)
    response = client.execute(mutation, variables=variables)
    data = response["data"]["completeSellerVerification"]

    assert data["status"] is False
    assert data["message"] == "Permission denied: Admin access required"


@pytest.mark.django_db
def test_complete_seller_verification_admin_success(client):
    mutation = """
    mutation CompleteSellerVerification($email: String!) {
        completeSellerVerification(email: $email) {
            status
            message
        }
    }
    """
    variables = {"email": "seller@example.com"}
    admin_user = UserFactory(is_staff=True)  # Create an admin user

    client.force_login(admin_user)
    with patch("users.models.ExtendUser.objects.get") as mock_user:
        mock_user.return_value = Mock(id=1, email="seller@example.com")
        response = client.execute(mutation, variables=variables)
        data = response["data"]["completeSellerVerification"]

        assert data["status"] is True
        assert data["message"] == "Successful"
