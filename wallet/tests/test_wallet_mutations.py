import pytest
from wallet.models import Wallet, WalletTransaction
from bill.models import Payment


@pytest.mark.django_db
def test_fund_wallet_success(client, valid_token, wallet, payment):
    mutation = """
        mutation FundWallet($token: String!, $remark: String!, $paymentRef: String!) {
            fundWallet(token: $token, remark: $remark, paymentRef: $paymentRef) {
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
        "remark": "Test Funding",
        "paymentRef": "valid_ref",
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["fundWallet"]["status"] is True
    assert response["data"]["fundWallet"]["message"] == "Wallet funded"
    assert response["data"]["fundWallet"]["wallet"]["balance"] == 1500


@pytest.mark.django_db
def test_fund_wallet_invalid_payment_ref(client, valid_token, wallet):
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
    assert response["data"]["fundWallet"]["status"] is False
    assert "Invalid Payment reference" in response["data"]["fundWallet"]["message"]


@pytest.mark.django_db
def test_withdraw_from_wallet_success(client, valid_token, wallet):
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
    assert response["data"]["withdrawFromWallet"]["status"] is True
    assert response["data"]["withdrawFromWallet"]["message"] == "Withdrawal successful"
    assert response["data"]["withdrawFromWallet"]["wallet"]["balance"] == 500


@pytest.mark.django_db
def test_withdraw_from_wallet_insufficient_balance(client, valid_token, wallet):
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
    assert response["data"]["withdrawFromWallet"]["status"] is False
    assert "Insufficient balance" in response["data"]["withdrawFromWallet"]["message"]
