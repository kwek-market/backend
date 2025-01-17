import pytest
from django.contrib.auth import get_user_model
from django.db import transaction
from graphene.test import Client
from graphene_django.utils.testing import GraphQLTestCase

from market.models import Category, Keyword, Product, ProductImage, ProductOption
from market.mutation import CreateProduct, ProductClick
from users.schema import schema

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create(username="admin", password="password", is_admin=True)


@pytest.fixture
def product(user):
    category = Category.objects.create(name="Electronics")
    return Product.objects.create(
        product_title="Test Product", category=category, user=user, price=100.00
    )


@pytest.fixture
def product(user):
    category = Category.objects.create(name="Electronics")
    return Product.objects.create(
        product_title="Test Product", category=category, user=user, price=100.00
    )


def test_delete_product_success(client, user, product):
    query = """
    mutation DeleteProduct($token: String!, $productId: String!) {
        deleteProduct(token: $token, id: $productId) {
            status
            message
        }
    }
    """
    variables = {"token": "fake_token_for_admin", "productId": str(product.id)}

    response = client.execute(query, variables=variables)
    data = response.get("data")["deleteProduct"]

    assert data["status"] is True
    assert data["message"] == "delete successful"


def test_delete_product_not_found(client, user):
    query = """
    mutation DeleteProduct($token: String!, $productId: String!) {
        deleteProduct(token: $token, id: $productId) {
            status
            message
        }
    }
    """
    variables = {"token": "fake_token_for_admin", "productId": "nonexistent_product_id"}

    response = client.execute(query, variables=variables)
    data = response.get("data")["deleteProduct"]

    assert data["status"] is False
    assert data["message"] == "product not found"


def test_delete_product_not_authorized(client, user, product):
    query = """
    mutation DeleteProduct($token: String!, $productId: String!) {
        deleteProduct(token: $token, id: $productId) {
            status
            message
        }
    }
    """
    user.token = "fake_token_for_non_admin"
    variables = {"token": user.token, "productId": str(product.id)}

    response = client.execute(query, variables=variables)
    data = response.get("data")["deleteProduct"]

    assert data["status"] is False
    assert data["message"] == "you are not allowed to delete this product"


@pytest.fixture
def client():
    return Client(schema)


def test_update_product_success(client, user, product):
    query = """
    mutation UpdateProduct($token: String!, $productId: String!, $productTitle: String!) {
        updateProduct(token: $token, productId: $productId, productTitle: $productTitle) {
            status
            message
            product {
                productTitle
            }
        }
    }
    """
    variables = {
        "token": "fake_token_for_admin",
        "productId": str(product.id),
        "productTitle": "Updated Product Title",
    }

    response = client.execute(query, variables=variables)
    data = response.get("data")["updateProduct"]

    assert data["status"] is True
    assert data["message"] == "update successful"
    assert data["product"]["productTitle"] == "Updated Product Title"


def test_update_product_not_found(client, user):
    query = """
    mutation UpdateProduct($token: String!, $productId: String!) {
        updateProduct(token: $token, productId: $productId) {
            status
            message
        }
    }
    """
    variables = {"token": "fake_token_for_admin", "productId": "nonexistent_product_id"}

    response = client.execute(query, variables=variables)
    data = response.get("data")["updateProduct"]

    assert data["status"] is False
    assert data["message"] == "product not found"


def test_update_product_not_authorized(client, user, product):
    query = """
    mutation UpdateProduct($token: String!, $productId: String!, $productTitle: String!) {
        updateProduct(token: $token, productId: $productId, productTitle: $productTitle) {
            status
            message
        }
    }
    """
    user.token = "fake_token_for_non_admin"
    variables = {
        "token": user.token,
        "productId": str(product.id),
        "productTitle": "New Title",
    }

    response = client.execute(query, variables=variables)
    data = response.get("data")["updateProduct"]

    assert data["status"] is False
    assert data["message"] == "you are not allowed to update this product"


@pytest.mark.django_db
class TestProductMutations(GraphQLTestCase):

    # Helper function to create test category
    def create_category(self, name="Test Category", visibility="visible", icon=None):
        return Category.objects.create(name=name, visibility=visibility, icon=icon)

    def create_product(
        self, token, product_title, category_id, subcategory_id, keyword_list, **kwargs
    ):
        query = """
            mutation CreateProduct(
                $token: String!, 
                $product_title: String!, 
                $category: String!, 
                $subcategory: String!, 
                $keyword: [String!]!
            ) {
                createProduct(
                    token: $token, 
                    productTitle: $product_title, 
                    category: $category, 
                    subcategory: $subcategory, 
                    keyword: $keyword
                ) {
                    status
                    message
                }
            }
        """
        variables = {
            "token": token,
            "product_title": product_title,
            "category": category_id,
            "subcategory": subcategory_id,
            "keyword": keyword_list,
        }
        return self.client.execute(query, variables=variables)

    # Test Case: Create Product Mutation
    def test_create_product(self):
        category = self.create_category(
            name="Test Category", visibility="visible", icon="icon_url"
        )
        subcategory = self.create_category(
            name="Subcategory", visibility="visible", icon="icon_url"
        )
        token = "valid_token"
        product_title = "Test Product"
        keyword_list = ["keyword1", "keyword2"]

        response = self.create_product(
            token, product_title, category.id, subcategory.id, keyword_list
        )

        assert response["data"]["createProduct"]["status"] == True
        assert response["data"]["createProduct"]["message"] == "Product added"

    # Test Case: Invalid Category for Create Product Mutation
    def test_create_product_invalid_category(self):
        subcategory = self.create_category(
            name="Subcategory", visibility="visible", icon="icon_url"
        )
        token = "valid_token"
        product_title = "Test Product"
        invalid_category_id = "invalid_category_id"
        keyword_list = ["keyword1", "keyword2"]

        response = self.create_product(
            token, product_title, invalid_category_id, subcategory.id, keyword_list
        )

        assert response["data"]["createProduct"]["status"] == False
        assert response["data"]["createProduct"]["message"] == "category not found"

    # Test Case: Product Click Mutation
    def test_product_click(self):
        product = Product.objects.create(
            product_title="Test Product",
            category=self.create_category().id,
            subcategory=self.create_category().id,
            charge_five_percent_vat=True,
            promoted=False,
            clicks=0,
        )
        token = "valid_token"

        # First, simulate a product click
        query = """
            mutation ProductClick($token: String, $productId: String!) {
                productClick(token: $token, productId: $productId) {
                    status
                    message
                }
            }
        """
        variables = {"token": token, "productId": product.id}

        response = self.client.execute(query, variables=variables)

        assert response["data"]["productClick"]["status"] == True
        assert response["data"]["productClick"]["message"] == "Click added"

        # Check if the click count increased
        product.refresh_from_db()
        assert product.clicks == 1

    # Test Case: Product Click Mutation - Invalid Product
    def test_product_click_invalid_product(self):
        token = "valid_token"
        invalid_product_id = "invalid_product_id"

        query = """
            mutation ProductClick($token: String, $productId: String!) {
                productClick(token: $token, productId: $productId) {
                    status
                    message
                }
            }
        """
        variables = {"token": token, "productId": invalid_product_id}

        response = self.client.execute(query, variables=variables)

        assert response["data"]["productClick"]["status"] == False
        assert response["data"]["productClick"]["message"] == "Invalid Product"
