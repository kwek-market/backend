import pytest
from graphene.test import Client
from users.schema import schema
from market.models import Product, User
from wallet.models import Wallet
from django.contrib.auth import get_user_model

User = get_user_model()
@pytest.fixture
def create_user():
    user = User.objects.create_user(username="testuser", password="password")
    return user


@pytest.fixture
def create_product(create_user):
    product = Product.objects.create(
        user=create_user, name="Test Product", description="Test Product Description"
    )
    return product


@pytest.fixture
def authenticate_user(create_user):
    # Returns a valid authentication token (you should implement token creation)
    return "valid_token"


@pytest.mark.django_db
def test_promote_product_success(create_product, authenticate_user):
    query = """
    mutation PromoteProduct($token: String!, $productId: String!, $days: Int!, $amount: Float!) {
        promoteProduct(token: $token, productId: $productId, days: $days, amount: $amount) {
            status
            message
            product {
                id
                promoted
            }
        }
    }
    """
    variables = {
        "token": authenticate_user,
        "productId": str(create_product.id),
        "days": 5,
        "amount": 100.00,
    }

    client = Client(schema)
    response = client.execute(query, variables=variables)

    assert response["data"]["promoteProduct"]["status"] is True
    assert response["data"]["promoteProduct"]["message"] == "Product promoted"
    assert response["data"]["promoteProduct"]["product"]["promoted"] is True


@pytest.mark.django_db
def test_promote_product_insufficient_balance(create_product, authenticate_user):
    query = """
    mutation PromoteProduct($token: String!, $productId: String!, $days: Int!, $amount: Float!) {
        promoteProduct(token: $token, productId: $productId, days: $days, amount: $amount) {
            status
            message
            product {
                id
                promoted
            }
        }
    }
    """
    variables = {
        "token": authenticate_user,
        "productId": str(create_product.id),
        "days": 5,
        "amount": 1000.00,  # Insufficient balance
    }

    client = Client(schema)
    response = client.execute(query, variables=variables)

    assert response["data"]["promoteProduct"]["status"] is False
    assert response["data"]["promoteProduct"]["message"] == "Insufficient balance"


@pytest.mark.django_db
def test_promote_product_invalid_product(create_user, authenticate_user):
    query = """
    mutation PromoteProduct($token: String!, $productId: String!, $days: Int!, $amount: Float!) {
        promoteProduct(token: $token, productId: $productId, days: $days, amount: $amount) {
            status
            message
        }
    }
    """
    variables = {
        "token": authenticate_user,
        "productId": "invalid_product_id",  # Invalid product ID
        "days": 5,
        "amount": 100.00,
    }

    client = Client(schema)
    response = client.execute(query, variables=variables)

    assert response["data"]["promoteProduct"]["status"] is False
    assert response["data"]["promoteProduct"]["message"] == "Product does not exist"


@pytest.mark.django_db
def test_cancel_product_promotion_success(create_product, authenticate_user):
    # Assume there's an active promotion for the product
    query = """
    mutation CancelProductPromotion($token: String!, $productId: String!) {
        cancelProductPromotion(token: $token, productId: $productId) {
            status
            message
        }
    }
    """
    variables = {"token": authenticate_user, "productId": str(create_product.id)}

    client = Client(schema)
    response = client.execute(query, variables=variables)

    assert response["data"]["cancelProductPromotion"]["status"] is True
    assert (
        response["data"]["cancelProductPromotion"]["message"] == "Promotion Cancelled"
    )


@pytest.mark.django_db
def test_cancel_product_promotion_invalid_user(create_product, authenticate_user):
    # Assume the user is not the product owner
    query = """
    mutation CancelProductPromotion($token: String!, $productId: String!) {
        cancelProductPromotion(token: $token, productId: $productId) {
            status
            message
        }
    }
    """
    variables = {
        "token": "invalid_token",  # Different user
        "productId": str(create_product.id),
    }

    client = Client(schema)
    response = client.execute(query, variables=variables)

    assert response["data"]["cancelProductPromotion"]["status"] is False
    assert (
        response["data"]["cancelProductPromotion"]["message"]
        == "Product does not belong to you"
    )
