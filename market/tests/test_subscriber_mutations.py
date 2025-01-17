import pytest
import graphene
from graphene_django.utils.testing import GraphQLTestCase
from market.models import (
    Newsletter,
    ContactMessage,
    Wishlist,
    Cart,
    Product,
    ProductOption,
)
from market.mutation import CreateSubscriber, ContactUs, WishListMutation, CreateCartItem


# Create Subscriber Test Case
@pytest.mark.django_db
class TestCreateSubscriber(GraphQLTestCase):

    def test_create_subscriber(self):
        query = """
        mutation CreateSubscriber($email: String!) {
            createSubscriber(email: $email) {
                status
                message
            }
        }
        """
        variables = {"email": "test@example.com"}

        response = self.client.execute(query, variables=variables)
        self.assertResponseNoErrors(response)
        self.assertEqual(response["data"]["createSubscriber"]["status"], True)
        self.assertEqual(
            response["data"]["createSubscriber"]["message"], "Subscription Successful"
        )

    def test_duplicate_subscriber(self):
        # Create a subscriber manually in the database first
        Newsletter.objects.create(email="test@example.com")

        query = """
        mutation CreateSubscriber($email: String!) {
            createSubscriber(email: $email) {
                status
                message
            }
        }
        """
        variables = {"email": "test@example.com"}

        response = self.client.execute(query, variables=variables)
        self.assertResponseNoErrors(response)
        self.assertEqual(response["data"]["createSubscriber"]["status"], False)
        self.assertEqual(
            response["data"]["createSubscriber"]["message"],
            "You have already subscribed",
        )


# Contact Us Test Case
@pytest.mark.django_db
class TestContactUs(GraphQLTestCase):

    def test_send_contact_message(self):
        query = """
        mutation ContactUs($email: String!, $name: String!, $message: String!) {
            contactUs(email: $email, name: $name, message: $message) {
                status
                message
            }
        }
        """
        variables = {
            "email": "test@example.com",
            "name": "Test User",
            "message": "I need help with my account.",
        }

        response = self.client.execute(query, variables=variables)
        self.assertResponseNoErrors(response)
        self.assertEqual(response["data"]["contactUs"]["status"], True)
        self.assertEqual(
            response["data"]["contactUs"]["message"], "message successfully sent"
        )

    def test_duplicate_contact_message(self):
        ContactMessage.objects.create(
            email="test@example.com",
            name="Test User",
            message="I need help with my account.",
        )

        query = """
        mutation ContactUs($email: String!, $name: String!, $message: String!) {
            contactUs(email: $email, name: $name, message: $message) {
                status
                message
            }
        }
        """
        variables = {
            "email": "test@example.com",
            "name": "Test User",
            "message": "I need help with my account.",
        }

        response = self.client.execute(query, variables=variables)
        self.assertResponseNoErrors(response)
        self.assertEqual(response["data"]["contactUs"]["status"], False)
        self.assertEqual(
            response["data"]["contactUs"]["message"],
            "You have already sent this message",
        )


# Wishlist Mutation Test Case
@pytest.mark.django_db
class TestWishListMutation(GraphQLTestCase):

    def test_add_to_wishlist(self):
        # Assuming `Product` and `User` are properly set up
        product = Product.objects.create(name="Test Product")
        user = self.create_user()  # Create a test user using your method
        token = self.get_token(user)  # Get auth token for the test user

        query = """
        mutation WishListMutation($token: String!, $productId: String!) {
            wishListMutation(token: $token, productId: $productId) {
                status
                message
            }
        }
        """
        variables = {"token": token, "productId": str(product.id)}

        response = self.client.execute(query, variables=variables)
        self.assertResponseNoErrors(response)
        self.assertEqual(response["data"]["wishListMutation"]["status"], True)
        self.assertEqual(response["data"]["wishListMutation"]["message"], "Successful")

    def test_remove_from_wishlist(self):
        # Add a product to wishlist first
        product = Product.objects.create(name="Test Product")
        user = self.create_user()  # Create a test user using your method
        token = self.get_token(user)  # Get auth token for the test user

        wishlist = Wishlist.objects.create(user=user)
        WishListItem.objects.create(wishlist=wishlist, product=product)

        query = """
        mutation WishListMutation($token: String!, $productId: String!) {
            wishListMutation(token: $token, productId: $productId) {
                status
                message
            }
        }
        """
        variables = {"token": token, "productId": str(product.id)}

        response = self.client.execute(query, variables=variables)
        self.assertResponseNoErrors(response)
        self.assertEqual(response["data"]["wishListMutation"]["status"], True)
        self.assertEqual(response["data"]["wishListMutation"]["message"], "Successful")


# Cart Mutation Test Case
@pytest.mark.django_db
class TestCreateCartItem(GraphQLTestCase):

    def test_add_product_to_cart(self):
        product_option = ProductOption.objects.create(price=100, discounted_price=90)
        product = Product.objects.create(name="Test Product")
        product.options.add(product_option)

        query = """
        mutation CreateCartItem($token: String!, $productOptionId: String!, $quantity: Int!) {
            createCartItem(token: $token, productOptionId: $productOptionId, quantity: $quantity) {
                status
                message
            }
        }
        """
        variables = {
            "token": "test_token",
            "productOptionId": str(product_option.id),
            "quantity": 2,
        }

        response = self.client.execute(query, variables=variables)
        self.assertResponseNoErrors(response)
        self.assertEqual(response["data"]["createCartItem"]["status"], True)
        self.assertEqual(response["data"]["createCartItem"]["message"], "Added to cart")

    def test_product_not_found(self):
        query = """
        mutation CreateCartItem($token: String!, $productOptionId: String!, $quantity: Int!) {
            createCartItem(token: $token, productOptionId: $productOptionId, quantity: $quantity) {
                status
                message
            }
        }
        """
        variables = {
            "token": "test_token",
            "productOptionId": "non_existent_id",
            "quantity": 2,
        }

        response = self.client.execute(query, variables=variables)
        self.assertResponseNoErrors(response)
        self.assertEqual(response["data"]["createCartItem"]["status"], False)
        self.assertEqual(
            response["data"]["createCartItem"]["message"], "product option not found"
        )
