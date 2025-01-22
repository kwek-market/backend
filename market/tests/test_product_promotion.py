import time

import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from graphene.test import Client

from market.models import Category, Product
from users.schema import schema
from wallet.models import Wallet

User = get_user_model()


@pytest.fixture
def create_category():
    category = Category.objects.create(name="Electronics")
    return category


@pytest.fixture
def create_user():
    user = User.objects.create_user(username="testuser", password="testpassword")
    return user


@pytest.fixture
def authenticate_user(create_user):
    payload = {
        "username": create_user.email,
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


@pytest.fixture
def create_product(create_user, create_category):
    product = Product.objects.create(
        user=create_user,
        product_title="Test Product",
        category=create_category,
        brand="Test Brand",
        product_weight="1kg",
        short_description="This is a test product",
        charge_five_percent_vat=True,
        promoted=False,
        keyword=["electronics", "test"]
    )
    return product


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
        "amount": 1000.00,  # Exceeding available balance
    }

    client = Client(schema)
    response = client.execute(query, variables=variables)

    assert response["data"]["promoteProduct"]["status"] is False
    assert response["data"]["promoteProduct"]["message"] == "Insufficient balance"


@pytest.mark.django_db
def test_promote_product_invalid_product(authenticate_user):
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
        "productId": "invalid_product_id",
        "days": 5,
        "amount": 100.00,
    }

    client = Client(schema)
    response = client.execute(query, variables=variables)

    assert response["data"]["promoteProduct"]["status"] is False
    assert response["data"]["promoteProduct"]["message"] == "Product does not exist"


@pytest.mark.django_db
def test_cancel_product_promotion_success(create_product, authenticate_user):
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
        response["data"]["cancelProductPromotion"]["message"] == "Promotion cancelled"
    )


@pytest.mark.django_db
def test_cancel_product_promotion_invalid_user(create_product):
    query = """
    mutation CancelProductPromotion($token: String!, $productId: String!) {
        cancelProductPromotion(token: $token, productId: $productId) {
            status
            message
        }
    }
    """
    # Using an invalid token to simulate an unauthorized request
    variables = {"token": "invalid_token", "productId": str(create_product.id)}

    client = Client(schema)
    response = client.execute(query, variables=variables)

    assert response["data"]["cancelProductPromotion"]["status"] is False
    assert response["data"]["cancelProductPromotion"]["message"] == "Unauthorized user"
