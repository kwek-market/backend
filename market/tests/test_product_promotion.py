# import pytest


# @pytest.mark.django_db
# def test_promote_product_success(
#     client, authenticate_user, create_product, create_wallet
# ):
#     query = """
#     mutation PromoteProduct($token: String!, $productId: String!, $days: Int!, $amount: Float!) {
#         promoteProduct(token: $token, productId: $productId, days: $days, amount: $amount) {
#             status
#             message
#             product {
#                 id
#                 promoted
#             }
#         }
#     }
#     """
#     variables = {
#         "token": authenticate_user,
#         "productId": str(create_product.id),
#         "days": 5,
#         "amount": 100.00,
#     }

#     response = client.execute(query, variables=variables)

#     assert response["data"]["promoteProduct"]["status"] is True
#     assert response["data"]["promoteProduct"]["message"] == "Product promoted"
#     assert response["data"]["promoteProduct"]["product"]["promoted"] is True


# @pytest.mark.django_db
# def test_promote_product_insufficient_balance(
#     client, authenticate_user, create_product
# ):
#     query = """
#     mutation PromoteProduct($token: String!, $productId: String!, $days: Int!, $amount: Float!) {
#         promoteProduct(token: $token, productId: $productId, days: $days, amount: $amount) {
#             status
#             message
#             product {
#                 id
#                 promoted
#             }
#         }
#     }
#     """
#     variables = {
#         "token": authenticate_user,
#         "productId": str(create_product.id),
#         "days": 5,
#         "amount": 1000.00,  # Exceeding available balance
#     }

#     response = client.execute(query, variables=variables)

#     assert response["data"]["promoteProduct"]["status"] is False
#     assert response["data"]["promoteProduct"]["message"] == "Insufficient balance"


# @pytest.mark.django_db
# def test_promote_product_invalid_product(client, authenticate_user):
#     query = """
#     mutation PromoteProduct($token: String!, $productId: String!, $days: Int!, $amount: Float!) {
#         promoteProduct(token: $token, productId: $productId, days: $days, amount: $amount) {
#             status
#             message
#         }
#     }
#     """
#     variables = {
#         "token": authenticate_user,
#         "productId": "invalid_product_id",
#         "days": 5,
#         "amount": 100.00,
#     }

#     response = client.execute(query, variables=variables)

#     assert response["data"]["promoteProduct"]["status"] is False
#     assert response["data"]["promoteProduct"]["message"] == "Product does not exist"


# @pytest.mark.django_db
# def test_cancel_product_promotion_success(client, authenticate_user, create_product):
#     query = """
#     mutation CancelProductPromotion($token: String!, $productId: String!) {
#         cancelProductPromotion(token: $token, productId: $productId) {
#             status
#             message
#         }
#     }
#     """
#     variables = {"token": authenticate_user, "productId": str(create_product.id)}

#     response = client.execute(query, variables=variables)

#     assert response["data"]["cancelProductPromotion"]["status"] is True
#     assert (
#         response["data"]["cancelProductPromotion"]["message"] == "Promotion cancelled"
#     )


# @pytest.mark.django_db
# def test_cancel_product_promotion_invalid_user(client, create_product):
#     query = """
#     mutation CancelProductPromotion($token: String!, $productId: String!) {
#         cancelProductPromotion(token: $token, productId: $productId) {
#             status
#             message
#         }
#     }
#     """
#     # Using an invalid token to simulate an unauthorized request
#     variables = {"token": "invalid_token", "productId": str(create_product.id)}

#     response = client.execute(query, variables=variables)

#     assert response["data"]["cancelProductPromotion"]["status"] is False
#     assert response["data"]["cancelProductPromotion"]["message"] == "Unauthorized user"
