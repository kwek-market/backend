import pytest
from graphene.test import Client
from users.schema import schema
from django.contrib.auth import get_user_model
from market.models import Cart, Wishlist
from notifications.models import Notification


@pytest.mark.django_db
class TestCreateUser:
    def user_data():
        return {
            "email": "testuser@example.com",
            "full_name": "Test User",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
        }


    @pytest.fixture
    def client():
        return Client(schema)


    def test_create_user(client, user_data):
        # Mutation to create user
        mutation = """
        mutation CreateUser($email: String!, $full_name: String!, $password1: String!, $password2: String!) {
            createUser(email: $email, fullName: $full_name, password1: $password1, password2: $password2) {
                status
                message
            }
        }
        """
        variables = user_data
        response = client.execute(mutation, variables=variables)

        # Check that the user creation was successful
        assert response["data"]["createUser"]["status"] is True
        assert (
            "Successfully created account for" in response["data"]["createUser"]["message"]
        )

        # Check if the user is actually created in the database
        user = get_user_model().objects.get(email=user_data["email"])
        assert user is not None
        assert user.is_verified is False  # Assuming the user is not verified immediately

        # Check if Cart and Wishlist are created
        assert Cart.objects.filter(user=user).exists()
        assert Wishlist.objects.filter(user=user).exists()
        assert Notification.objects.filter(user=user).exists()


    def test_create_user_invalid_email(client, user_data):
        user_data["email"] = "invalidemail.com"
        mutation = """
        mutation CreateUser($email: String!, $full_name: String!, $password1: String!, $password2: String!) {
            createUser(email: $email, fullName: $full_name, password1: $password1, password2: $password2) {
                status
                message
            }
        }
        """
        variables = user_data
        response = client.execute(mutation, variables=variables)

        assert response["data"]["createUser"]["status"] is False
        assert "Invalid email" in response["data"]["createUser"]["message"]


@pytest.mark.django_db
class TestLoginUser:
def test_login_user(client, user_data):
    # Create user first
    user = get_user_model().objects.create_user(
        email=user_data["email"],
        full_name=user_data["full_name"],
        password=user_data["password1"],
    )

    # Mutation to login user
    mutation = """
    mutation LoginUser($email: String!, $password: String!, $ip: String!) {
        loginUser(email: $email, password: $password, ip: $ip) {
            status
            token
            message
        }
    }
    """
    variables = {
        "email": user_data["email"],
        "password": user_data["password1"],
        "ip": "192.168.0.1",
    }
    response = client.execute(mutation, variables=variables)

    # Check if login is successful and a token is returned
    assert response["data"]["loginUser"]["status"] is True
    assert "You logged in successfully." in response["data"]["loginUser"]["message"]
    assert "token" in response["data"]["loginUser"]

    def test_login_user_with_unverified_email(client, user_data):
    # Create user but don't verify email
    user = get_user_model().objects.create_user(
        email=user_data["email"],
        full_name=user_data["full_name"],
        password=user_data["password1"],
    )

    # Mutation to login user
    mutation = """
    mutation LoginUser($email: String!, $password: String!, $ip: String!) {
        loginUser(email: $email, password: $password, ip: $ip) {
            status
            message
        }
    }
    """
    variables = {
        "email": user_data["email"],
        "password": user_data["password1"],
        "ip": "192.168.0.1",
    }
    response = client.execute(mutation, variables=variables)

    # Check if error message is returned for unverified email
    assert response["data"]["loginUser"]["status"] is False
    assert "Your email is not verified" in response["data"]["loginUser"]["message"]




@pytest.mark.django_db
class TestEmailVerification:
    def test_resend_verification_email(client, user_data):
    # Create user first
    user = get_user_model().objects.create_user(
        email=user_data["email"],
        full_name=user_data["full_name"],
        password=user_data["password1"],
    )

    mutation = """
    mutation ResendVerification($email: String!) {
        resendVerification(email: $email) {
            status
            message
        }
    }
    """
    variables = {"email": user_data["email"]}
    response = client.execute(mutation, variables=variables)

    # Check if resend verification email was sent successfully
    assert response["data"]["resendVerification"]["status"] is True
    assert (
        "Successfully sent email to"
        in response["data"]["resendVerification"]["message"]
    )

@pytest.mark.django_db
class TestChangePassword:
    def test_change_password(client, user_data):
        # Create user first
        user = get_user_model().objects.create_user(
            email=user_data["email"],
            full_name=user_data["full_name"],
            password=user_data["password1"],
        )

        # Login user to get token (reuse login mutation)
        mutation = """
        mutation LoginUser($email: String!, $password: String!, $ip: String!) {
            loginUser(email: $email, password: $password, ip: $ip) {
                token
            }
        }
        """
        variables = {
            "email": user_data["email"],
            "password": user_data["password1"],
            "ip": "192.168.0.1",
        }
        response = client.execute(mutation, variables=variables)
        token = response["data"]["loginUser"]["token"]

        # Mutation to change user password
        mutation = """
        mutation ChangePassword($token: String!, $password1: String!, $password2: String!) {
            changePassword(token: $token, password1: $password1, password2: $password2) {
                status
                message
            }
        }
        """
        variables = {
            "token": token,
            "password1": "NewPassword123!",
            "password2": "NewPassword123!",
        }
        response = client.execute(mutation, variables=variables)

        # Check if password change was successful
        assert response["data"]["changePassword"]["status"] is True
        assert (
            "Password changed successfully" in response["data"]["changePassword"]["message"]
        )
