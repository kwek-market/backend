import pytest
from wallet.models import Wallet, WalletTransaction
from bill.models import Payment
import uuid

# @pytest.mark.django_db
# def test_fund_wallet_success(client, valid_token, wallet, payment):
#     # Set initial balance and verify
#     initial_balance = 1000
#     wallet.balance = initial_balance
#     wallet.save()
#     assert Wallet.objects.get(id=wallet.id).balance == initial_balance

#     # Set payment amount
#     payment.amount = 500
#     payment.verified = True
#     payment.used = False
#     payment.save()

#     mutation = """
#     mutation FundWallet($token: String!, $remark: String!, $paymentRef: String!) {
#         fundWallet(token: $token, remark: $remark, paymentRef: $paymentRef) {
#             status
#             message
#             wallet {
#                 id
#                 balance
#             }
#         }
#     }
#     """

#     variables = {
#         "token": valid_token,
#         "remark": "Test Funding",
#         "paymentRef": str(uuid.uuid4),
#     }

#     response = client.execute(mutation, variables=variables)

#     # Refresh wallet from database to get updated balance
#     wallet.refresh_from_db()

#     assert response["data"]["fundWallet"]["status"] is True
#     assert response["data"]["fundWallet"]["message"] == "Wallet funded"
#     assert response["data"]["fundWallet"]["wallet"]["balance"] == 1500
#     assert wallet.balance == 1500  # Verify actual database balance


@pytest.mark.django_db
def test_fund_wallet_invalid_payment_ref(client, valid_token, wallet):
    # Set and verify initial balance
    initial_balance = 1000
    wallet.balance = initial_balance
    wallet.save()

    mutation = """
    mutation FundWallet($token: String!, $remark: String!, $paymentRef: String!) {
        fundWallet(token: $token, remark: $remark, paymentRef: $paymentRef) {
            status
            message
        }
    }
    """

    variables = {
        "token": valid_token,
        "remark": "Test Funding",
        "paymentRef": "invalid_ref",
    }

    response = client.execute(mutation, variables=variables)

    # Refresh wallet and verify balance hasn't changed
    wallet.refresh_from_db()
    assert wallet.balance == initial_balance
    assert response["data"]["fundWallet"]["status"] is False
    assert "Invalid Payment reference" in response["data"]["fundWallet"]["message"]


@pytest.mark.django_db
def test_withdraw_from_wallet_success(client, valid_token, wallet):
    # Set and verify initial balance
    initial_balance = 1000
    wallet.balance = initial_balance
    wallet.save()
    assert Wallet.objects.get(id=wallet.id).balance == initial_balance

    mutation = """
    mutation WithdrawFromWallet($token: String!, $password: String!, $amount: Int!) {
        withdrawFromWallet(token: $token, password: $password, amount: $amount) {
            status
            message
            wallet {
                id
                balance
            }
        }
    }
    """

    variables = {
        "token": valid_token,
        "password": "password123",
        "amount": 500,
    }

    response = client.execute(mutation, variables=variables)

    # Refresh wallet from database
    wallet.refresh_from_db()

    assert response["data"]["withdrawFromWallet"]["status"] is True
    assert response["data"]["withdrawFromWallet"]["message"] == "Withdrawal successful"
    assert response["data"]["withdrawFromWallet"]["wallet"]["balance"] == 500
    assert wallet.balance == 500  # Verify actual database balance


@pytest.mark.django_db
def test_withdraw_from_wallet_insufficient_balance(client, valid_token, wallet):
    # Set and verify initial balance
    initial_balance = 1000
    wallet.balance = initial_balance
    wallet.save()
    assert Wallet.objects.get(id=wallet.id).balance == initial_balance

    mutation = """
    mutation WithdrawFromWallet($token: String!, $password: String!, $amount: Int!) {
        withdrawFromWallet(token: $token, password: $password, amount: $amount) {
            status
            message
        }
    }
    """

    variables = {
        "token": valid_token,
        "password": "password123",
        "amount": 1500,
    }

    response = client.execute(mutation, variables=variables)

    # Refresh wallet and verify balance hasn't changed
    wallet.refresh_from_db()
    assert wallet.balance == initial_balance
    assert response["data"]["withdrawFromWallet"]["status"] is False
    assert "Insufficient balance" in response["data"]["withdrawFromWallet"]["message"]
