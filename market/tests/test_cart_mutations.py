# import pytest
# from market.models import Cart, CartItem


# @pytest.mark.django_db
# class TestDeleteCartMutation:
#     def test_delete_cart_by_token(
#         self, client, cart, valid_token, delete_cart_mutation
#     ):
#         variables = {"cartId": str(cart.id), "token": valid_token}

#         response = client.execute(delete_cart_mutation, variables=variables)

#         assert response.get("data", {}).get("deleteCart", {}).get("status") is True
#         assert (
#             response.get("data", {}).get("deleteCart", {}).get("message")
#             == "Deleted successfully"
#         )
#         assert not Cart.objects.filter(id=cart.id).exists()

#     def test_delete_cart_by_ip(self, client, cart_with_ip, delete_cart_mutation):
#         variables = {"cartId": str(cart_with_ip.id), "ip": "192.168.0.1"}

#         response = client.execute(delete_cart_mutation, variables=variables)

#         assert response.get("data", {}).get("deleteCart", {}).get("status") is True
#         assert (
#             response.get("data", {}).get("deleteCart", {}).get("message")
#             == "Deleted successfully"
#         )
#         assert not Cart.objects.filter(id=cart_with_ip.id).exists()

#     def test_delete_cart_invalid_authentication(
#         self, client, cart, delete_cart_mutation
#     ):
#         variables = {"cartId": str(cart.id), "token": "invalid_token"}

#         response = client.execute(delete_cart_mutation, variables=variables)

#         assert response.get("data", {}).get("deleteCart", {}).get("status") is False
#         assert (
#             response.get("data", {}).get("deleteCart", {}).get("message")
#             == "invalid authentication token"
#         )
#         assert Cart.objects.filter(id=cart.id).exists()


# @pytest.mark.django_db
# class TestDecreaseCartItemQuantityMutation:
#     def test_decrease_cart_item_quantity(
#         self, client, cart, cart_item, valid_token, decrease_cart_item_quantity_mutation
#     ):
#         variables = {
#             "cartId": str(cart.id),
#             "itemId": str(cart_item.id),
#             "token": valid_token,
#         }

#         response = client.execute(
#             decrease_cart_item_quantity_mutation, variables=variables
#         )

#         assert (
#             response.get("data", {}).get("decreaseCartItemQuantity", {}).get("status")
#             is True
#         )
#         assert (
#             response.get("data", {}).get("decreaseCartItemQuantity", {}).get("message")
#             == "Quantity reduced successfully"
#         )

#         cart_item.refresh_from_db()
#         assert cart_item.quantity == 4

#     def test_decrease_cart_item_to_zero(
#         self, client, cart, cart_item, valid_token, decrease_cart_item_quantity_mutation
#     ):
#         cart_item.quantity = 1
#         cart_item.save()

#         variables = {
#             "cartId": str(cart.id),
#             "itemId": str(cart_item.id),
#             "token": valid_token,
#         }

#         response = client.execute(
#             decrease_cart_item_quantity_mutation, variables=variables
#         )

#         assert (
#             response.get("data", {}).get("decreaseCartItemQuantity", {}).get("status")
#             is True
#         )
#         assert (
#             response.get("data", {}).get("decreaseCartItemQuantity", {}).get("message")
#             == "Item removed from cart"
#         )
#         assert not CartItem.objects.filter(id=cart_item.id).exists()


# @pytest.mark.django_db
# class TestRemoveItemFromCartWithOptionIdMutation:
#     def test_remove_item_from_cart(
#         self, client, cart_item, valid_token, remove_item_from_cart_mutation
#     ):
#         variables = {
#             "productOptionId": cart_item.product_option_id,
#             "quantity": 1,
#             "token": valid_token,
#         }

#         response = client.execute(remove_item_from_cart_mutation, variables=variables)

#         assert (
#             response.get("data", {})
#             .get("removeItemFromCartWithOptionId", {})
#             .get("status")
#             is True
#         )
#         assert (
#             response.get("data", {})
#             .get("removeItemFromCartWithOptionId", {})
#             .get("message")
#             == "Item removed successfully"
#         )

#         cart_item.refresh_from_db()
#         assert cart_item.quantity == 4

#     def test_remove_nonexistent_item(
#         self, client, valid_token, remove_item_from_cart_mutation
#     ):
#         variables = {
#             "productOptionId": "nonexistent-id",
#             "quantity": 1,
#             "token": valid_token,
#         }

#         response = client.execute(remove_item_from_cart_mutation, variables=variables)

#         assert (
#             response.get("data", {})
#             .get("removeItemFromCartWithOptionId", {})
#             .get("status")
#             is False
#         )
#         assert (
#             response.get("data", {})
#             .get("removeItemFromCartWithOptionId", {})
#             .get("message")
#             == "Cart not found"
#         )
