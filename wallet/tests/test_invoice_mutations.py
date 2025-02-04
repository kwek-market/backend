import pytest
import json
from wallet.models import Invoice, PurchasedItem


@pytest.mark.django_db
def test_create_invoice_success(client, valid_token, store_detail):
    mutation = """
        mutation CreateInvoice($token: String!, $customerName: String!, $customerEmail: String!, $customerAddress: String!, $purchasedItem: [String!]!, $deliveryFee: Int!, $subtotal: Int!, $total: Int!, $note: String) {
            createInvoice(
                token: $token,
                customerName: $customerName,
                customerEmail: $customerEmail,
                customerAddress: $customerAddress,
                purchasedItem: $purchasedItem,
                deliveryFee: $deliveryFee,
                subtotal: $subtotal,
                total: $total,
                note: $note
            ) {
                status
                message
                invoice {
                    id
                    customerName
                    customerEmail
                }
            }
        }
    """
    purchased_item = [
        json.dumps(
            {
                "item": "Test Item",
                "description": "Test Description",
                "quantity": 2,
                "unit_cost": 100,
                "total": 200,
            }
        )
    ]
    variables = {
        "token": valid_token,
        "customerName": "Test Customer",
        "customerEmail": "customer@example.com",
        "customerAddress": "123 Test Street",
        "purchasedItem": purchased_item,
        "deliveryFee": 50,
        "subtotal": 200,
        "total": 250,
        "note": "Test Note",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["createInvoice"]["status"] is True
    assert response["data"]["createInvoice"]["message"] == "Invoice created"
    assert (
        response["data"]["createInvoice"]["invoice"]["customerName"] == "Test Customer"
    )


@pytest.mark.django_db
def test_create_invoice_invalid_user(client):
    mutation = """
        mutation CreateInvoice($token: String!, $customerName: String!, $customerEmail: String!, $customerAddress: String!, $purchasedItem: [String!]!, $deliveryFee: Int!, $subtotal: Int!, $total: Int!, $note: String) {
            createInvoice(
                token: $token,
                customerName: $customerName,
                customerEmail: $customerEmail,
                customerAddress: $customerAddress,
                purchasedItem: $purchasedItem,
                deliveryFee: $deliveryFee,
                subtotal: $subtotal,
                total: $total,
                note: $note
            ) {
                status
                message
            }
        }
    """
    variables = {
        "token": "invalid_token",
        "customerName": "Test Customer",
        "customerEmail": "customer@example.com",
        "customerAddress": "123 Test Street",
        "purchasedItem": [],
        "deliveryFee": 50,
        "subtotal": 200,
        "total": 250,
        "note": "Test Note",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["createInvoice"]["status"] is False
    assert "invalid authentication token" in response["data"]["createInvoice"]["message"]
