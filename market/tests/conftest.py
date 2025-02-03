import time
import jwt
import pytest
from django.contrib.auth import get_user_model
from graphene.test import Client
from django.conf import settings
from market.models import (
    Newsletter,
    ContactMessage,
    Wishlist,
    Cart,
    Product,
    ProductOption,
)
from users.schema import schema

User = get_user_model()


@pytest.fixture
def client():
    return Client(schema)


@pytest.fixture
def create_user():
    """
    Fixture to create a standard test user.
    """

    def _create_user(
        email="testuser@example.com", password="password123", is_admin=False
    ):
        user = User.objects.create_user(
            email=email, password=password, is_admin=is_admin, is_verified=True
        )
        return user

    return _create_user


@pytest.fixture
def get_token():
    """
    Fixture to generate an authentication token for a user.
    """

    def _get_token(user):
        current_time = int(time.time())
        payload = {
            "username": user.email,
            "exp": current_time + 3600,  # Token valid for 1 hour
            "origIat": current_time,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token

    return _get_token


@pytest.fixture
def valid_token(create_user, get_token):
    """
    Generates a valid admin token for testing.
    """
    admin_user = create_user(email="admin@example.com", is_admin=True)
    return get_token(admin_user)


@pytest.fixture
def invalid_token():
    """
    Generates an invalid token for testing.
    """
    current_time = int(time.time())
    payload = {
        "username": "fake_user@example.com",
        "exp": current_time + 3600,
        "origIat": current_time,
    }
    # Use a different secret key to make the token invalid
    invalid_secret_key = "invalid_secret_key"
    token = jwt.encode(payload, invalid_secret_key, algorithm="HS256")
    return token


@pytest.fixture
def state_fee_id():
    """
    Returns a valid state fee ID for testing purposes.
    """
    return "valid_state_fee_id"


@pytest.fixture
def product():
    """
    Creates a test product.
    """
    return Product.objects.create(name="Test Product")


@pytest.fixture
def product_option(product):
    """
    Creates a test product option linked to a product.
    """
    option = ProductOption.objects.create(price=100, discounted_price=90)
    product.options.add(option)
    return option


@pytest.fixture
def wishlist(create_user, product):
    """
    Creates a wishlist and adds a product.
    """
    user = create_user()
    wishlist = Wishlist.objects.create(user=user)
    return wishlist


@pytest.fixture
def newsletter():
    """
    Creates a sample newsletter subscriber.
    """
    return Newsletter.objects.create(email="test@example.com")


@pytest.fixture
def contact_message():
    """
    Creates a sample contact message.
    """
    return ContactMessage.objects.create(
        email="test@example.com",
        name="Test User",
        message="I need help with my account.",
    )
