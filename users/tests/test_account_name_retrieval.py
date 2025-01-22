# import pytest
# from unittest.mock import patch
# from graphene.test import Client
# from users.schema import schema


# @pytest.mark.django_db
# def test_account_name_retrieval_success(client):
#     mutation = """
#     mutation AccountNameRetrieval($accountNumber: String!, $bankCode: String!) {
#         accountNameRetrieval(accountNumber: $accountNumber, bankCode: $bankCode) {
#             status
#             message
#             accountNumber
#             accountName
#         }
#     }
#     """
#     variables = {"accountNumber": "1234567890", "bankCode": "001"}

#     with patch("users.utils.send_post_request") as mock_send_request:
#         mock_send_request.return_value = {
#             "status": "success",
#             "message": "Account found",
#             "data": {"account_number": "1234567890", "account_name": "John Doe"},
#         }

#         response = client.execute(mutation, variables=variables)
#         data = response["data"]["accountNameRetrieval"]

#         assert data["status"] is True
#         assert data["accountNumber"] == "1234567890"
#         assert data["accountName"] == "John Doe"


# @pytest.mark.django_db
# def test_account_name_retrieval_error(client):
#     mutation = """
#     mutation AccountNameRetrieval($accountNumber: String!, $bankCode: String!) {
#         accountNameRetrieval(accountNumber: $accountNumber, bankCode: $bankCode) {
#             status
#             message
#             accountNumber
#             accountName
#         }
#     }
#     """
#     variables = {"accountNumber": "9876543210", "bankCode": "999"}

#     with patch("users.utils.send_post_request") as mock_post_request:
#         mock_post_request.return_value = {
#             "status": "error",
#             "message": "Invalid bank code",
#         }

#         response = client.execute(mutation, variables=variables)
#         data = response["data"]["accountNameRetrieval"]

#         assert data["status"] is False
#         assert data["message"] == "Invalid bank code"
#         assert data["accountNumber"] == "null"
#         assert data["accountName"] == "null"
