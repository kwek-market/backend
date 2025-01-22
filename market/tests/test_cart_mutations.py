# import graphene
# import pytest
# from graphene_django.utils.testing import graphql_query
# from market.models import Cart, CartItem, Product, User, Wishlist


# @pytest.mark.django_db
# class TestDeleteCartMutation:
#     def test_delete_cart_by_token(self):
#         # Create a user and a cart
#         user = User.objects.create_user(email="test@example.com", password="password")
#         cart = Cart.objects.create(user=user)

#         # Define the mutation query
#         mutation = """
#         mutation DeleteCart($cartId: String!, $token: String) {
#             deleteCart(cartId: $cartId, token: $token) {
#                 status
#                 message
#             }
#         }
#         """

#         # Set the input variables
#         variables = {
#             "cartId": str(cart.id),
#             "token": user.token,  # assuming the user has a valid token
#         }

#         # Perform the query
#         response = graphql_query(mutation, variables=variables)

#         # Assert the response
#         assert response["data"]["deleteCart"]["status"] is True
#         assert response["data"]["deleteCart"]["message"] == "Deleted successfully"

#     def test_delete_cart_invalid_token(self):
#         # Create a user and a cart
#         user = User.objects.create_user(email="test@example.com", password="password")
#         cart = Cart.objects.create(user=user)

#         # Define the mutation query
#         mutation = """
#         mutation DeleteCart($cartId: String!, $token: String) {
#             deleteCart(cartId: $cartId, token: $token) {
#                 status
#                 message
#             }
#         }
#         """

#         # Set the input variables with an invalid token
#         variables = {"cartId": str(cart.id), "token": "invalid_token"}

#         # Perform the query
#         response = graphql_query(mutation, variables=variables)

#         # Assert the response
#         assert response["data"]["deleteCart"]["status"] is False
#         assert response["data"]["deleteCart"]["message"] == "Invalid user"

#     def test_delete_cart_by_ip(self):
#         # Create a cart with IP
#         cart = Cart.objects.create(ip="192.168.0.1")

#         # Define the mutation query
#         mutation = """
#         mutation DeleteCart($cartId: String!, $ip: String) {
#             deleteCart(cartId: $cartId, ip: $ip) {
#                 status
#                 message
#             }
#         }
#         """

#         # Set the input variables
#         variables = {"cartId": str(cart.id), "ip": "192.168.0.1"}

#         # Perform the query
#         response = graphql_query(mutation, variables=variables)

#         # Assert the response
#         assert response["data"]["deleteCart"]["status"] is True
#         assert response["data"]["deleteCart"]["message"] == "Deleted successfully"

#     def test_delete_cart_invalid_ip(self):
#         # Create a cart with a different IP
#         cart = Cart.objects.create(ip="192.168.0.2")

#         # Define the mutation query
#         mutation = """
#         mutation DeleteCart($cartId: String!, $ip: String) {
#             deleteCart(cartId: $cartId, ip: $ip) {
#                 status
#                 message
#             }
#         }
#         """

#         # Set the input variables with an invalid IP
#         variables = {"cartId": str(cart.id), "ip": "192.168.0.1"}

#         # Perform the query
#         response = graphql_query(mutation, variables=variables)

#         # Assert the response
#         assert response["data"]["deleteCart"]["status"] is False
#         assert response["data"]["deleteCart"]["message"] == "Invalid user"


# @pytest.mark.django_db
# class TestDecreaseCartItemQuantityMutation:
#     def test_decrease_cart_item_quantity(self):
#         # Create a user, product, cart, and cart item
#         user = User.objects.create_user(email="test@example.com", password="password")
#         product = Product.objects.create(name="Product 1")
#         cart = Cart.objects.create(user=user)
#         cart_item = CartItem.objects.create(cart=cart, product=product, quantity=5)

#         # Define the mutation query
#         mutation = """
#         mutation DecreaseCartItemQuantity($cartId: String!, $itemId: String!, $token: String) {
#             decreaseCartItemQuantity(cartId: $cartId, itemId: $itemId, token: $token) {
#                 status
#                 message
#                 cartItem {
#                     quantity
#                 }
#             }
#         }
#         """

#         # Set the input variables
#         variables = {
#             "cartId": str(cart.id),
#             "itemId": str(cart_item.id),
#             "token": user.token,  # assuming the user has a valid token
#         }

#         # Perform the query
#         response = graphql_query(mutation, variables=variables)

#         # Assert the response
#         assert response["data"]["decreaseCartItemQuantity"]["status"] is True
#         assert (
#             response["data"]["decreaseCartItemQuantity"]["message"]
#             == "Quantity reduced successfully"
#         )
#         assert response["data"]["decreaseCartItemQuantity"]["cartItem"]["quantity"] == 4

#     def test_decrease_cart_item_quantity_invalid_item(self):
#         # Create a user and cart
#         user = User.objects.create_user(email="test@example.com", password="password")
#         cart = Cart.objects.create(user=user)

#         # Define the mutation query
#         mutation = """
#         mutation DecreaseCartItemQuantity($cartId: String!, $itemId: String!, $token: String) {
#             decreaseCartItemQuantity(cartId: $cartId, itemId: $itemId, token: $token) {
#                 status
#                 message
#             }
#         }
#         """

#         # Set the input variables with an invalid item ID
#         variables = {
#             "cartId": str(cart.id),
#             "itemId": "invalid_item_id",
#             "token": user.token,
#         }

#         # Perform the query
#         response = graphql_query(mutation, variables=variables)

#         # Assert the response
#         assert response["data"]["decreaseCartItemQuantity"]["status"] is False
#         assert (
#             response["data"]["decreaseCartItemQuantity"]["message"]
#             == "Cart Item does not exist"
#         )


# @pytest.mark.django_db
# class TestRemoveItemFromCartWithOptionIdMutation:
#     def test_remove_item_from_cart_with_option_id(self):
#         # Create a user, cart, product option, and cart item
#         user = User.objects.create_user(email="test@example.com", password="password")
#         product = Product.objects.create(name="Product 1")
#         cart = Cart.objects.create(user=user)
#         cart_item = CartItem.objects.create(
#             cart=cart, product=product, product_option_id="option_1", quantity=5
#         )

#         # Define the mutation query
#         mutation = """
#         mutation RemoveItemFromCartWithOptionId($productOptionId: String!, $quantity: Int!, $token: String) {
#             removeItemFromCartWithOptionId(productOptionId: $productOptionId, quantity: $quantity, token: $token) {
#                 status
#                 message
#             }
#         }
#         """

#         # Set the input variables
#         variables = {
#             "productOptionId": "option_1",
#             "quantity": 1,
#             "token": user.token,  # assuming the user has a valid token
#         }

#         # Perform the query
#         response = graphql_query(mutation, variables=variables)

#         # Assert the response
#         assert response["data"]["removeItemFromCartWithOptionId"]["status"] is True
#         assert (
#             response["data"]["removeItemFromCartWithOptionId"]["message"]
#             == "successful"
#         )


# @pytest.mark.django_db
# class TestDeleteCartItemMutation:
#     def test_delete_cart_item(self):
#         # Create a user, cart, product, and cart item
#         user = User.objects.create_user(email="test@example.com", password="password")
#         product = Product.objects.create(name="Product 1")
#         cart = Cart.objects.create(user=user)
#         cart_item = CartItem.objects.create(cart=cart, product=product, quantity=5)

#         # Define the mutation query
#         mutation = """
#         mutation DeleteCartItem($cartId: String!, $itemId: String!, $token: String) {
#             deleteCartItem(cartId: $cartId, itemId: $itemId, token: $token) {
#                 status
#                 message
#             }
#         }
#         """

#         # Set the input variables
#         variables = {
#             "cartId": str(cart.id),
#             "itemId": str(cart_item.id),
#             "token": user.token,
#         }

#         # Perform the query
#         response = graphql_query(mutation, variables=variables)

#         # Assert the response
#         assert response["data"]["deleteCartItem"]["status"] is True
#         assert response["data"]["deleteCartItem"]["message"] == "Deleted successfully"
