from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from graphene.test import Client

from notifications.models import Notification
from users.models import ExtendUser, SellerProfile
from users.schema import schema
from wallet.models import StoreDetail, Wallet


# Fixture for the GraphQL client
@pytest.fixture
def client():
    return Client(schema)


# Fixture for creating a user
@pytest.fixture
def user_factory():
    User = get_user_model()

    def create_user(email, is_staff=False):
        return User.objects.create(
            email=email, is_staff=is_staff, username=email, is_seller=True
        )

    return create_user


# @pytest.mark.django_db
# def test_complete_seller_verification_success(client, user_factory):
#     mutation = """
#     mutation CompleteSellerVerification($email: String!) {
#         completeSellerVerification(email: $email) {
#             status
#             message
#         }
#     }
#     """
#     variables = {"email": "sellerautoverify@example.com"}

#     with patch("users.models.ExtendUser.objects.get") as mock_user, patch(
#         "users.models.SellerProfile.objects.get"
#     ) as mock_seller, patch(
#         "wallet.models.StoreDetail.objects.filter"
#     ) as mock_store_filter, patch(
#         "wallet.models.Wallet.objects.filter"
#     ) as mock_wallet_filter, patch(
#         "notifications.models.Notification.objects.filter"
#     ) as mock_notification_filter, patch(
#         "market.pusher.push_to_client"
#     ), patch(
#         "market.pusher.SendEmailNotification"
#     ):

#         mock_user.return_value = Mock(id=1, email="seller@example.com")
#         mock_seller.return_value = Mock(
#             seller_is_verified=False,
#             seller_is_rejected=False,
#             shop_name="Test Shop",
#             shop_address="123 Test Street",
#         )
#         mock_store_filter.return_value.exists.return_value = False
#         mock_wallet_filter.return_value.exists.return_value = False
#         mock_notification_filter.return_value.exists.return_value = False

#         response = client.execute(mutation, variables=variables)
#         data = response["data"]["completeSellerVerification"]

#         assert data["status"] is True
#         assert data["message"] == "Successful"


@pytest.mark.django_db
def test_complete_seller_verification_not_a_seller(client, user_factory):
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


# @pytest.mark.django_db
# def test_complete_seller_verification_error(client, user_factory):
#     mutation = """
#     mutation CompleteSellerVerification($email: String!) {
#         completeSellerVerification(email: $email) {
#             status
#             message
#         }
#     }
#     """
#     variables = {"email": "error@example.com"}

#     with patch(
#         "users.models.ExtendUser.objects.get", side_effect=Exception("Unexpected error")
#     ):
#         response = client.execute(mutation, variables=variables)
#         data = response["data"]["completeSellerVerification"]

#         assert data["status"] is False
#         assert "Unexpected error" in data["message"]


# @pytest.mark.django_db
# def test_complete_seller_verification_permission_denied(client, user_factory):
#     mutation = """
#     mutation CompleteSellerVerification($email: String!) {
#         completeSellerVerification(email: $email) {
#             status
#             message
#         }
#     }
#     """
#     variables = {"email": "seller@example.com"}
#     user = user_factory(email="non_admin@example.com", is_staff=False)  # Non-admin user

#     with patch("users.models.ExtendUser.objects.get"):
#         response = client.execute(mutation, variables=variables)
#         data = response["data"]["completeSellerVerification"]

#         assert data["status"] is False
#         assert data["message"] == "Permission denied: Admin access required"


# @pytest.mark.django_db
# def test_complete_seller_verification_admin_success(client, user_factory):
#     mutation = """
#     mutation CompleteSellerVerification($email: String!) {
#         completeSellerVerification(email: $email) {
#             status
#             message
#         }
#     }
#     """
#     variables = {"email": "seller@example.com"}
#     admin_user = user_factory(email="admin@example.com", is_staff=True)  # Admin user

#     with patch("users.models.ExtendUser.objects.get") as mock_user:
#         mock_user.return_value = Mock(id=1, email="seller@example.com")
#         response = client.execute(mutation, variables=variables)
#         data = response["data"]["completeSellerVerification"]

#         assert data["status"] is True
#         assert data["message"] == "Successful"
