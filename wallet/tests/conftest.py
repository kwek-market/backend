import time

import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

from bill.models import Payment
from market.models import Product
from notifications.models import Message, Notification
from users.models import ExtendUser, SellerProfile
from wallet.models import PurchasedItem, StoreDetail, Wallet, WalletTransaction, Order, WalletRefund
from market.models import Cart, CartItem
User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="test@example.com",
        password="password123",
        username="test@example.com",
    )


@pytest.fixture
def seller_profile(user):
    return SellerProfile.objects.create(
        user=user,
        shop_name="Test Shop",
        shop_address="123 Test Street",
        accepted_policy=True, 
    )


@pytest.fixture
def store_detail(user, seller_profile):
    return StoreDetail.objects.create(
        user=user,
        store_name=seller_profile.shop_name,
        email=user.email,
        address=seller_profile.shop_address,
    )


@pytest.fixture
def wallet(user):
    return Wallet.objects.create(owner=user, balance=1000)


@pytest.fixture
def payment(user):
    return Payment.objects.create(
        ref="valid_ref",
        amount=500,
        verified=True,
        used=False,
        user_id=user,
    )


@pytest.fixture
def valid_token(user):
    payload = {
        "username": user.email,
        "exp": int(time.time()) + 3600,  # Token valid for 1 hour
        "origIat": int(time.time()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256").decode("utf-8")


@pytest.fixture
def order(user, cart_item):
    order = Order.objects.create(user=user)
    order.cart_items.add(cart_item)
    return order


@pytest.fixture
def cart_item(user):
    product = Product.objects.create(
        product_title="Test Product",
        user=user,
        charge_five_percent_vat = False,
        keyword = []
    )
    return CartItem.objects.create(
        product=product,
        quantity=1,
        price=100,
    )


@pytest.fixture
def wallet_refund(order, cart_item):
    return WalletRefund.objects.create(
        order=order,
        product=cart_item,
        account_number="1234567890",
        bank_name="Test Bank",
        number_of_product=1,
    )


@pytest.fixture
def client():
    from graphene.test import Client

    from users.schema import schema

    return Client(schema)
