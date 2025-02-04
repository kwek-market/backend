import pytest
import uuid
from market.models import Product
from users.models import ExtendUser
from wallet.models import  Order, Wallet, WalletRefund, WalletTransaction
from market.models import CartItem

@pytest.mark.django_db
def test_wallet_transaction_success(client, valid_token, wallet):
    # Create a wallet transaction
    wallet_transaction = WalletTransaction.objects.create(
        wallet=wallet,
        amount=100,
        remark="Test Transaction",
        transaction_type="Funding",
        status=False,
    )

    mutation = """
        mutation WalletTransactionSuccess($token: String!, $walletTransactionId: String!) {
            walletTransactionSuccess(token: $token, walletTransactionId: $walletTransactionId) {
                status
                message
                wallet {
                    id
                }
            }
        }
    """
    variables = {
        "token": valid_token,
        "walletTransactionId": str(wallet_transaction.id),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["walletTransactionSuccess"]["status"] is True
    assert (
        response["data"]["walletTransactionSuccess"]["message"]
        == "Transaction processed successfully"
    )
    assert WalletTransaction.objects.get(id=wallet_transaction.id).status is True


@pytest.mark.django_db
def test_wallet_transaction_success_invalid_id(client, valid_token):
    mutation = """
        mutation WalletTransactionSuccess($token: String!, $walletTransactionId: String!) {
            walletTransactionSuccess(token: $token, walletTransactionId: $walletTransactionId) {
                status
                message
            }
        }
    """
    variables = {
        "token": valid_token,
        "walletTransactionId": str(uuid.uuid4()),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["walletTransactionSuccess"]["status"] is False
    assert (
        "Invalid transaction ID"
        in response["data"]["walletTransactionSuccess"]["message"]
    )


# @pytest.mark.django_db
# def test_refund_request_success(client, valid_token, order, cart_item):
#     mutation = """
#         mutation RefundRequest($token: String!, $orderId: String!, $cartItemId: String!, $accountNumber: String!, $bankName: String!, $numberOfProduct: String) {
#             refundRequest(
#                 token: $token,
#                 orderId: $orderId,
#                 cartItemId: $cartItemId,
#                 accountNumber: $accountNumber,
#                 bankName: $bankName,
#                 numberOfProduct: $numberOfProduct
#             ) {
#                 status
#                 message
#                 refund {
#                     id
#                 }
#             }
#         }
#     """
#     variables = {
#         "token": valid_token,
#         "orderId": str(order.id),
#         "cartItemId": str(cart_item.id),
#         "accountNumber": "1234567890",
#         "bankName": "Test Bank",
#         "numberOfProduct": "1",
#     }
#     response = client.execute(mutation, variables=variables)
#     assert response["data"]["refundRequest"]["status"] is True
#     assert response["data"]["refundRequest"]["message"] == "Refund in progress"
#     assert WalletRefund.objects.filter(order=order, product=cart_item).exists()


# @pytest.mark.django_db
# def test_refund_request_invalid_order(client, valid_token, cart_item):
#     mutation = """
#         mutation RefundRequest($token: String!, $orderId: String!, $cartItemId: String!, $accountNumber: String!, $bankName: String!, $numberOfProduct: String) {
#             refundRequest(
#                 token: $token,
#                 orderId: $orderId,
#                 cartItemId: $cartItemId,
#                 accountNumber: $accountNumber,
#                 bankName: $bankName,
#                 numberOfProduct: $numberOfProduct
#             ) {
#                 status
#                 message
#             }
#         }
#     """
#     variables = {
#         "token": valid_token,
#         "orderId": "invalid_order_id",
#         "cartItemId": str(cart_item.id),
#         "accountNumber": "1234567890",
#         "bankName": "Test Bank",
#         "numberOfProduct": "1",
#     }
#     response = client.execute(mutation, variables=variables)
#     print(response)
#     assert response["data"]["RefundRequest"]["status"] is False
#     assert "Could not find order" in response["data"]["RefundRequest"]["message"]


@pytest.mark.django_db
def test_force_refund_success(client, valid_token, wallet_refund, wallet):
    mutation = """
        mutation ForceRefund($token: String!, $refundId: String!) {
            forceRefund(token: $token, refundId: $refundId) {
                status
                message
            }
        }
    """
    variables = {
        "token": valid_token,
        "refundId": str(wallet_refund.id),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["forceRefund"]["status"] is True
    assert (
        response["data"]["forceRefund"]["message"]
        == "Amount successfully deducted from seller's wallet"
    )
    assert WalletRefund.objects.get(id=wallet_refund.id).status is True


@pytest.mark.django_db
def test_force_refund_already_refunded(client, valid_token, wallet_refund):
    wallet_refund.status = True                
    wallet_refund.save()

    mutation = """
        mutation ForceRefund($token: String!, $refundId: String!) {
            forceRefund(token: $token, refundId: $refundId) {
                status
                message
            }
        }
    """
    variables = {
        "token": valid_token,
        "refundId": str(wallet_refund.id),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["forceRefund"]["status"] is False
    assert "Already refunded" in response["data"]["forceRefund"]["message"]


@pytest.mark.django_db
def test_force_refund_invalid_id(client, valid_token):
    mutation = """
        mutation ForceRefund($token: String!, $refundId: String!) {
            forceRefund(token: $token, refundId: $refundId) {
                status
                message
            }
        }
    """
    # Generate a valid UUID that doesn't exist in the database
    non_existent_refund_id = str(uuid.uuid4())

    variables = {
        "token": valid_token,
        "refundId": non_existent_refund_id,
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["forceRefund"]["status"] is False
    assert "Refund does not exist" in response["data"]["forceRefund"]["message"]
