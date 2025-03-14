import time

import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from graphene.test import Client

from market.models import (
    Cart,
    CartItem,
    ContactMessage,
    Newsletter,
    Product,
    ProductOption,
    Wishlist,
    StateDeliveryFee,
)
from users.schema import schema

User = get_user_model()

@pytest.fixture
def client():
    return Client(schema)


@pytest.fixture
def user():
    user = User.objects.create_user(
        email="testuser@example.com",
        username="testuser@example.com",
        password="password123",
        is_admin=False,
    )
    return user


@pytest.fixture
def admin_user():
    admin_user = User.objects.create_user(
        email="admintestuser@example.com",
        username="admintestuser@example.com",
        password="password123",
        is_admin=True,
    )
    return admin_user


@pytest.fixture
def cart(user):
    cart = Cart.objects.create(user=user)
    return cart


@pytest.fixture
def product(user):
    return Product.objects.create(
        product_title="Test Product",
        user=user,
        charge_five_percent_vat=False,  # Add this field
        keyword=[],  # Add this field
    )


@pytest.fixture
def product_option(product):
    return ProductOption.objects.create(
        product=product,
        quantity=10,
        price=100.0,
    )


@pytest.fixture
def cart_item(cart, product_option):
    return CartItem.objects.create(
        cart=cart,
        product=product_option.product,
        product_option_id=str(product_option.id),
        quantity=5,
        price=product_option.price,
        ordered=False,
    )


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
def valid_token(user, get_token):
    """
    Generates a valid admin token for testing.
    """
    return get_token(user)


@pytest.fixture
def admin_token(admin_user, get_token):
    """
    Generates a valid admin token for testing.
    """
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
    return StateDeliveryFee.objects.create()


@pytest.fixture
def wishlist(user, product):
    """
    Creates a wishlist and adds a product.
    """
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

# Add these fixtures after your existing ones


@pytest.fixture
def cart_with_ip():
    """
    Creates a cart associated with an IP address instead of a user.
    """
    return Cart.objects.create(ip="127.0.0.1")


@pytest.fixture
def decrease_cart_item_quantity_mutation():
    """
    GraphQL mutation for decreasing cart item quantity.
    """
    return """
    mutation($cartId: String!, $productOptionId: String!, $token: String) {
        decreaseCartItemQuantity(cartId: $cartId, productOptionId: $productOptionId, token: $token) {
            status
            message
            cartItem {
                id
                quantity
                price
            }
        }
    }
    """


@pytest.fixture
def remove_item_from_cart_mutation():
    """
    GraphQL mutation for removing an item from cart.
    """
    return """
    mutation($productOptionId: String!, $quantity: Int, $token: String) {
        removeItemFromCartWithOptionId(productOptionId: $productOptionId, quantity: $quantity, token: $token) {
            status
            message
        }
    }
    """


@pytest.fixture
def delete_cart_mutation():
    return """
    mutation($cartId: String!, $token: String) {
        deleteCart(cartId: $cartId, token: $token) {
            status
            message
        }
    }
    """


@pytest.fixture
def delete_cart_mutation_by_ip():
    return """
    mutation($cartId: String!, $ip: String) {
        deleteCart(cartId: $cartId, ip: $ip) {
            status
            message
        }
    }
    """
