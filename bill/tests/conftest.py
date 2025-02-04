import secrets
import string
import time
from datetime import datetime, timedelta
import jwt
from django.conf import settings
import pytest
from django.utils import timezone

from bill.models import (
    Billing,
    Coupon,
    CouponUser,
    Order,
    OrderProgress,
    Payment,
    Pickup,
)
from market.models import Cart, CartItem, Product, ProductOption
from notifications.models import Message, Notification
from users.models import ExtendUser, SellerCustomer, SellerProfile
from wallet.models import Wallet


@pytest.fixture
def valid_payment_ref():
    return secrets.token_urlsafe(50)


@pytest.fixture
def valid_transaction_id():
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(12))


@pytest.fixture
def billing_mutation():
    return """
    mutation BillingAddress(
        $fullName: String!,
        $contact: String!,
        $address: String!,
        $state: String!,
        $city: String!,
        $token: String
    ) {
        billingAddress(
            fullName: $fullName,
            contact: $contact,
            address: $address,
            state: $state,
            city: $city,
            token: $token
        ) {
            status
            message
            billingAddress {
                id
                fullName
                contact
                address
                state
                city
            }
        }
    }
    """


@pytest.fixture
def user():
    return ExtendUser.objects.create_user(
        email="test@example.com",
        password="password123",
        username="test@example.com",
    )


@pytest.fixture
def valid_token(user):
    ct = int(time.time())
    payload = {
        "username": user.email, 
        "exp": ct + 151200,  
        "origIat": ct
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256").decode()

@pytest.fixture
def client():
    from graphene.test import Client

    from users.schema import schema

    return Client(schema)

@pytest.fixture
def admin_user():
    return ExtendUser.objects.create_user(
        email="admin@example.com",
        password="password123",
        username="admin@example.com",
        is_admin=True,
    )

@pytest.fixture
def admin_token(admin_user):
    ct = int(time.time())
    payload = {
        "username": admin_user.email, 
        "exp": ct + 151200,  
        "origIat": ct
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256").decode()

@pytest.fixture
def cart(user):
    return Cart.objects.create(user=user)


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
        quantity=2,
        price=product_option.price,
        ordered=False,  
    )


@pytest.fixture
def billing_address(user):
    return Billing.objects.create(
        full_name="John Doe",
        contact="1234567890",
        address="123 Test Street",
        state="Test State",
        city="Test City",
        user=user,
    )


@pytest.fixture
def order(user, cart_item, billing_address):
    return Order.objects.create(
        user=user,
        payment_method="pay on delivery",
        delivery_method="door step",
        door_step=billing_address,
        delivery_fee=50.0,
        cart_items=[cart_item],
    )


@pytest.fixture
def order_progress(order):
    return OrderProgress.objects.create(order=order, progress="Order in progress")


@pytest.fixture
def coupon():
    return Coupon.objects.create(
        value=10,
        valid_until=timezone.now() + timedelta(days=7),
        code="TEST10",
    )


@pytest.fixture
def expired_coupon():
    return Coupon.objects.create(
        value=10,
        valid_until=timezone.now() - timedelta(days=7),
        code="EXPIRED10",
    )
