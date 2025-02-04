# import pytest


# @pytest.mark.django_db
# def test_flash_sales_creation_success(client, create_product, authenticate_user):
#     query = """
#     mutation FlashSalesMutation($token: String!, $productOptionId: String!, $discountPercent: Float!, $days: Int!) {
#         flashSalesMutation(token: $token, productOptionId: $productOptionId, discountPercent: $discountPercent, days: $days) {
#             status
#             message
#             flashSales {
#                 id
#                 discountPercent
#                 status
#             }
#         }
#     }
#     """
#     variables = {
#         "token": authenticate_user,
#         "productOptionId": str(create_product.id),
#         "discountPercent": 20.0,
#         "days": 5,
#     }

#     response = client.execute(query, variables=variables)

#     assert response["data"]["flashSalesMutation"]["status"] is True
#     assert (
#         response["data"]["flashSalesMutation"]["message"]
#         == "Flash Sale created successfully"
#     )
#     assert (
#         response["data"]["flashSalesMutation"]["flashSales"]["discountPercent"] == 20.0
#     )


# @pytest.mark.django_db
# def test_flash_sales_already_exists(client, create_product, authenticate_user):
#     query = """
#     mutation FlashSalesMutation($token: String!, $productOptionId: String!, $discountPercent: Float!, $days: Int!) {
#         flashSalesMutation(token: $token, productOptionId: $productOptionId, discountPercent: $discountPercent, days: $days) {
#             status
#             message
#         }
#     }
#     """
#     variables = {
#         "token": authenticate_user,
#         "productOptionId": str(create_product.id),
#         "discountPercent": 10.0,
#         "days": 3,
#     }

#     response = client.execute(query, variables=variables)

#     # After first execution, the product already has a flash sale, so we expect this to fail
#     assert response["data"]["flashSalesMutation"]["status"] is True
#     assert (
#         response["data"]["flashSalesMutation"]["message"]
#         == "Flash Sale already created"
#     )
