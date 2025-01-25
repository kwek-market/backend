import pytest
from unittest.mock import patch
from graphene.test import Client
from users.schema import schema



@pytest.mark.django_db
def test_start_selling_success(client, user):
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
        "token": "valid_token",
        "firstname": "John",
        "lastname": "Doe",
        "phoneNumber": "1234567890",
        "shopName": "Doe's Shop",
        "shopUrl": "does-shop",
        "shopAddress": "123 Market St",
        "state": "California",
        "lga": "Los Angeles",
        "landmark": "Near Central Park",
        "howYouHeardAboutUs": "Internet",
        "acceptedPolicy": True,
    }

    with patch("users.utils.authenticate_user") as mock_auth, patch(
        "users.models.SellerProfile.objects.filter"
    ) as mock_filter:

        mock_auth.return_value = {"status": True, "user": user}
        mock_filter.return_value.exists.return_value = False

        response = client.execute(mutation, variables=variables)
        data = response["data"]["startSelling"]

        assert data["status"] is True
        assert data["message"] == "Seller account created successfully"


@pytest.mark.django_db
def test_start_selling_shop_url_taken(client, user):
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
        "token": "valid_token",
        "firstname": "John",
        "lastname": "Doe",
        "phoneNumber": "1234567890",
        "shopName": "Doe's Shop",
        "shopUrl": "does-shop",
        "shopAddress": "123 Market St",
        "state": "California",
        "lga": "Los Angeles",
        "landmark": "Near Central Park",
        "howYouHeardAboutUs": "Internet",
        "acceptedPolicy": True,
    }

    with patch("users.utils.authenticate_user") as mock_auth, patch(
        "users.models.SellerProfile.objects.filter"
    ) as mock_filter:

        mock_auth.return_value = {"status": True, "user": user}
        mock_filter.return_value.exists.return_value = True

        response = client.execute(mutation, variables=variables)
        data = response["data"]["startSelling"]

        assert data["status"] is False
        assert data["message"] == "Shop url already taken"
