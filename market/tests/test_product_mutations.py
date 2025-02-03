# import pytest


# @pytest.mark.django_db
# def test_delete_product_success(client, token, product):
#     query = """
#     mutation DeleteProduct($token: String!, $productId: String!) {
#         deleteProduct(token: $token, id: $productId) {
#             status
#             message
#         }
#     }
#     """
#     variables = {"token": token, "productId": str(product.id)}

#     response = client.execute(query, variables=variables)
#     data = response.get("data")["deleteProduct"]

#     assert data["status"] is True
#     assert data["message"] == "delete successful"


# @pytest.mark.django_db
# def test_delete_product_not_found(client, token):
#     query = """
#     mutation DeleteProduct($token: String!, $productId: String!) {
#         deleteProduct(token: $token, id: $productId) {
#             status
#             message
#         }
#     }
#     """
#     variables = {"token": token, "productId": "nonexistent_product_id"}

#     response = client.execute(query, variables=variables)
#     data = response.get("data")["deleteProduct"]

#     assert data["status"] is False
#     assert data["message"] == "product not found"


# @pytest.mark.django_db
# def test_delete_product_not_authorized(client, user_token, product):
#     query = """
#     mutation DeleteProduct($token: String!, $productId: String!) {
#         deleteProduct(token: $token, id: $productId) {
#             status
#             message
#         }
#     }
#     """
#     variables = {"token": user_token, "productId": str(product.id)}

#     response = client.execute(query, variables=variables)
#     data = response.get("data")["deleteProduct"]

#     assert data["status"] is False
#     assert data["message"] == "you are not allowed to delete this product"


# @pytest.mark.django_db
# def test_update_product_success(client, token, product):
#     query = """
#     mutation UpdateProduct($token: String!, $productId: String!, $productTitle: String!) {
#         updateProduct(token: $token, productId: $productId, productTitle: $productTitle) {
#             status
#             message
#             product {
#                 productTitle
#             }
#         }
#     }
#     """
#     variables = {
#         "token": token,
#         "productId": str(product.id),
#         "productTitle": "Updated Product Title",
#     }

#     response = client.execute(query, variables=variables)
#     data = response.get("data")["updateProduct"]

#     assert data["status"] is True
#     assert data["message"] == "update successful"
#     assert data["product"]["productTitle"] == "Updated Product Title"


# @pytest.mark.django_db
# def test_update_product_not_found(client, token):
#     query = """
#     mutation UpdateProduct($token: String!, $productId: String!, $productTitle: String!) {
#         updateProduct(token: $token, productId: $productId, productTitle: $productTitle) {
#             status
#             message
#         }
#     }
#     """
#     variables = {
#         "token": token,
#         "productId": "nonexistent_product_id",
#         "productTitle": "New Title",
#     }

#     response = client.execute(query, variables=variables)
#     data = response.get("data")["updateProduct"]

#     assert data["status"] is False
#     assert data["message"] == "product not found"


# @pytest.mark.django_db
# def test_update_product_not_authorized(client, user_token, product):
#     query = """
#     mutation UpdateProduct($token: String!, $productId: String!, $productTitle: String!) {
#         updateProduct(token: $token, productId: $productId, productTitle: $productTitle) {
#             status
#             message
#         }
#     }
#     """
#     variables = {
#         "token": user_token,
#         "productId": str(product.id),
#         "productTitle": "Unauthorized Title",
#     }

#     response = client.execute(query, variables=variables)
#     data = response.get("data")["updateProduct"]

#     assert data["status"] is False
#     assert data["message"] == "you are not allowed to update this product"
