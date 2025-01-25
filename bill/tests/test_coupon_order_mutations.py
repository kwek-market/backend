from datetime import datetime, timedelta

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
from market.models import Product, ProductOption, Cart,CartItem
from notifications.models import Message, Notification
from users.models import ExtendUser, SellerCustomer, SellerProfile
from wallet.models import Wallet
from bill.models import Coupon


@pytest.mark.django_db
def test_cancel_order_success(client, valid_token, order):
    mutation = """
        mutation CancelOrder($orderId: String!) {
            cancelOrder(orderId: $orderId) {
                status
                message
            }
        }
    """
    variables = {
        "orderId": str(order.id),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["cancelOrder"]["status"] is True
    assert response["data"]["cancelOrder"]["message"] == "Order cancelled"
    assert Order.objects.get(id=order.id).closed is True
    assert OrderProgress.objects.get(order=order).progress == "Order cancelled"


@pytest.mark.django_db
def test_cancel_order_invalid_id(client, valid_token):
    mutation = """
        mutation CancelOrder($orderId: String!) {
            cancelOrder(orderId: $orderId) {
                status
                message
            }
        }
    """
    variables = {
        "orderId": "invalid_order_id",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["cancelOrder"]["status"] is False
    assert "Invalid order id" in response["data"]["cancelOrder"]["message"]


@pytest.mark.django_db
def test_create_coupon_success(client, valid_token):
    mutation = """
        mutation CreateCoupon($value: Int!, $code: String, $days: Int, $validUntil: DateTime, $userList: [String!]) {
            createCoupon(value: $value, code: $code, days: $days, validUntil: $validUntil, userList: $userList) {
                status
                message
                coupon {
                    id
                    value
                    code
                    validUntil
                }
            }
        }
    """
    variables = {
        "value": 10,
        "code": "TEST10",
        "days": 7,
        "userList": [],
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["createCoupon"]["status"] is True
    assert response["data"]["createCoupon"]["message"] == "Coupon created successfully"
    assert response["data"]["createCoupon"]["coupon"]["value"] == 10


@pytest.mark.django_db
def test_create_coupon_invalid_input(client, valid_token):
    mutation = """
        mutation CreateCoupon($value: Int!, $code: String, $days: Int, $validUntil: DateTime, $userList: [String!]) {
            createCoupon(value: $value, code: $code, days: $days, validUntil: $validUntil, userList: $userList) {
                status
                message
            }
        }
    """
    variables = {
        "value": 10,
        "code": "TEST10",
        "days": 7,
        "validUntil": "2023-12-31T00:00:00Z",
        "userList": [],
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["createCoupon"]["status"] is False
    assert (
        "Please enter either number of days(int) or valid_until(datetime)"
        in response["data"]["createCoupon"]["message"]
    )


@pytest.mark.django_db
def test_apply_coupon_success(client, valid_token, user, coupon):
    mutation = """
        mutation ApplyCoupon($token: String!, $couponId: String!) {
            applyCoupon(token: $token, couponId: $couponId) {
                status
                message
                coupon {
                    id
                    value
                    code
                }
            }
        }
    """
    variables = {
        "token": valid_token,
        "couponId": str(coupon.id),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["applyCoupon"]["status"] is True
    assert response["data"]["applyCoupon"]["message"] == "Coupon redeemed"
    assert CouponUser.objects.filter(coupon=coupon, user=user).exists()


@pytest.mark.django_db
def test_apply_coupon_expired(client, valid_token, user, expired_coupon):
    mutation = """
        mutation ApplyCoupon($token: String!, $couponId: String!) {
            applyCoupon(token: $token, couponId: $couponId) {
                status
                message
            }
        }
    """
    variables = {
        "token": valid_token,
        "couponId": str(expired_coupon.id),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["applyCoupon"]["status"] is False
    assert "Coupon is expired" in response["data"]["applyCoupon"]["message"]


@pytest.mark.django_db
def test_unapply_coupon_success(client, valid_token, user, coupon):
    CouponUser.objects.create(coupon=coupon, user=user)
    mutation = """
        mutation UnapplyCoupon($token: String!, $couponIds: [String!]!) {
            unapplyCoupon(token: $token, couponIds: $couponIds) {
                status
                message
                coupon {
                    id
                    value
                    code
                }
            }
        }
    """
    variables = {
        "token": valid_token,
        "couponIds": [str(coupon.id)],
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["unapplyCoupon"]["status"] is True
    assert response["data"]["unapplyCoupon"]["message"] == "Coupon unapplied"
    assert not CouponUser.objects.filter(coupon=coupon, user=user).exists()


@pytest.mark.django_db
def test_delete_coupon_success(client, valid_token, admin_user, coupon):
    mutation = """
        mutation DeleteCoupon($token: String!, $couponId: String!) {
            deleteCoupon(token: $token, couponId: $couponId) {
                status
                message
            }
        }
    """
    variables = {
        "token": valid_token,
        "couponId": str(coupon.id),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["deleteCoupon"]["status"] is True
    assert response["data"]["deleteCoupon"]["message"] == "Coupon unapplied"
    assert not Coupon.objects.filter(id=coupon.id).exists()
