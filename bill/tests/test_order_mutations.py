import pytest
import uuid
from market.models import Order
@pytest.mark.django_db
def test_place_order_success(
    client, valid_token, user, cart, cart_item, billing_address
):
    mutation = """
        mutation PlaceOrder($token: String!, $cartId: String!, $paymentMethod: String!, $deliveryMethod: String!, $addressId: String!, $state: String!, $city: String!) {
            placeOrder(
                token: $token,
                cartId: $cartId,
                paymentMethod: $paymentMethod,
                deliveryMethod: $deliveryMethod,
                addressId: $addressId,
                state: $state,
                city: $city
            ) {
                status
                message
                orderId
                id
            }
        }
    """
    variables = {
        "token": valid_token,
        "cartId": str(cart.id),
        "paymentMethod": "pay on delivery",
        "deliveryMethod": "door step",
        "addressId": str(billing_address.id),
        "state": "Test State",
        "city": "Test City",
    }
    response = client.execute(mutation, variables=variables)
    
    assert response["data"]["placeOrder"]["status"] is True
    assert response["data"]["placeOrder"]["message"] == "Order placed successfully"
    assert Order.objects.filter(id=response["data"]["placeOrder"]["id"]).exists()


@pytest.mark.django_db
def test_place_order_invalid_cart(client, valid_token, user):
    mutation = """
        mutation PlaceOrder($token: String!, $cartId: String!, $paymentMethod: String!, $deliveryMethod: String!, $addressId: String!, $state: String!, $city: String!) {
            placeOrder(
                token: $token,
                cartId: $cartId,
                paymentMethod: $paymentMethod,
                deliveryMethod: $deliveryMethod,
                addressId: $addressId,
                state: $state,
                city: $city
            ) {
                status
                message
            }
        }
    """
    variables = {
        "token": valid_token,
        "cartId": str(uuid.uuid4()),
        "paymentMethod": "pay on delivery",
        "deliveryMethod": "door step",
        "addressId": str(uuid.uuid4()),
        "state": "Test State",
        "city": "Test City",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["placeOrder"]["status"] is False
    assert "Cart does not exist" in response["data"]["placeOrder"]["message"]


@pytest.mark.django_db
def test_track_order_success(client, valid_token, user, order):
    mutation = """
        mutation TrackOrder($orderId: String!) {
            trackOrder(orderId: $orderId) {
                status
                message
            }
        }
    """
    variables = {
        "orderId": str(order.order_id),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["trackOrder"]["status"] is True
    assert response["data"]["trackOrder"]["message"] == "Order Placed successfully"


@pytest.mark.django_db
def test_track_order_invalid_id(client, valid_token):
    mutation = """
        mutation TrackOrder($orderId: String!) {
            trackOrder(orderId: $orderId) {
                status
                message
            }
        }
    """
    variables = {
        "orderId": uuid.uuid4(),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["trackOrder"]["status"] is False
    assert "Invalid Order id" in response["data"]["trackOrder"]["message"]


@pytest.mark.django_db
def test_update_order_progress_success(client, valid_token, order):
    mutation = """
        mutation UpdateOrderProgress($orderId: String!, $progress: String!) {
            updateOrderProgress(orderId: $orderId, progress: $progress) {
                status
                message
            }
        }
    """
    variables = {
        "orderId": str(order.id),
        "progress": "Shipped",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["updateOrderProgress"]["status"] is True
    assert response["data"]["updateOrderProgress"]["message"] == "Shipped"


@pytest.mark.django_db
def test_update_order_progress_invalid_id(client, valid_token):
    mutation = """
        mutation UpdateOrderProgress($orderId: String!, $progress: String!) {
            updateOrderProgress(orderId: $orderId, progress: $progress) {
                status
                message
            }
        }
    """
    variables = {
        "orderId": str(uuid.uuid4()),
        "progress": "Shipped",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["updateOrderProgress"]["status"] is False
    assert "Invalid Order id" in response["data"]["updateOrderProgress"]["message"]


@pytest.mark.django_db
def test_update_delivery_status_success(client, valid_token, order):
    mutation = """
    mutation UpdateDeliveryStatus($orderId: String!, $deliveryStatus: String!) {
        updateDeliveryStatus(orderId: $orderId, deliveryStatus: $deliveryStatus) {
            status
            message
        }
    }
    """
    variables = {
        "orderId": str(order.id),
        "deliveryStatus": "delivered",
    }
    response = client.execute(mutation, variables=variables)
    print(response)
    assert response["data"]["updateDeliveryStatus"]["status"] is True
    assert (
        response["data"]["updateDeliveryStatus"]["message"] == "Delivery status updated"
    ) 


@pytest.mark.django_db
def test_update_delivery_status_invalid_id(client, valid_token):
    mutation = """
        mutation UpdateDeliveryStatus($orderId: String!, $deliveryStatus: String!) {
            updateDeliveryStatus(orderId: $orderId, deliveryStatus: $deliveryStatus) {
                status
                message
            }
        }
    """
    variables = {
        "orderId": str(uuid.uuid4()),
        "deliveryStatus": "delivered",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["updateDeliveryStatus"]["status"] is False
    assert "Invalid Order Id" in response["data"]["updateDeliveryStatus"]["message"]
