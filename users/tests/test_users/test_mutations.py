import time
from unittest.mock import patch

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase


class UserManagementTests(GraphQLTestCase):
    GRAPHQL_URL = "/v1/kwekql"

    def setUp(self):
        # Set up test user
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="Password123!",
            full_name="Test User",
            is_verified=True,
        )
        self.user_unverified = self.User.objects.create_user(
            username="unverifieduser",
            email="unverified@example.com",
            password="Password123!",
            full_name="Unverified User",
            is_verified=False,
        )
        # JWT token for testing
        self.token = jwt.encode(
            {"user": self.user.email}, settings.SECRET_KEY, algorithm="HS256"
        )

    def test_create_user_invalid_email(self):
        response = self.query(
            """
            mutation {
                createUser(
                    password1: "Password123!",
                    password2: "Password123!",
                    fullName: "Invalid Email User",
                    email: "invalidemail.com"
                ) {
                    status
                    message
                }
            }
            """
        )
        content = response.json()
        self.assertFalse(content["data"]["createUser"]["status"])
        self.assertIn("Enter Valid E-mail", content["data"]["createUser"]["message"])

    def test_create_user_duplicate_email(self):
        # Create a user first
        self.User.objects.create_user(
            username="duplicateuser",
            email="duplicate@example.com",
            password="Password123!",
            full_name="Duplicate User",
        )

        # Try to create another user with the same email
        response = self.query(
            """
            mutation {
                createUser(
                    password1: "Password123!",
                    password2: "Password123!",
                    fullName: "New User",
                    email: "duplicate@example.com"
                ) {
                    status
                    message
                }
            }
            """
        )
        content = response.json()
        self.assertFalse(content["data"]["createUser"]["status"])
        self.assertIn(
            "E-mail Already in use", content["data"]["createUser"]["message"]
        )

    @patch("users.auth_mutation.send_confirmation_email")
    def test_resend_verification_email_success(self, mock_send_email):
        mock_send_email.return_value = {"status": True}
        response = self.query(
            """
            mutation {
                resendVerification(email: "testuser@example.com") {
                    status
                    message
                }
            }
            """
        )
        content = response.json()
        self.assertTrue(content["data"]["resendVerification"]["status"])
        self.assertIn(
            "Successfully sent email to testuser@example.com",
            content["data"]["resendVerification"]["message"],
        )

    def test_resend_verification_email_invalid(self):
        response = self.query(
            """
            mutation {
                resendVerification(email: "nonexistent@example.com") {
                    status
                    message
                }
            }
            """
        )
        content = response.json()
        print(content)
        self.assertFalse(content["data"]["resendVerification"]["status"])
        self.assertIn(
            "No user with this email found",
            content["data"]["resendVerification"]["message"],
        )

    def test_create_user_success(self):
        response = self.query(
            """
            mutation {
                createUser(
                    password1: "Password123!",
                    password2: "Password123!",
                    fullName: "New User",
                    email: "newuser@example.com"
                ) {
                    status
                    message
                }
            }
            """
        )
        content = response.json()
        self.assertTrue(content["data"]["createUser"]["status"])
        self.assertEqual(
            content["data"]["createUser"]["message"],
            "Successfully created account for, newuser@example.com",
        )
        self.assertTrue(self.User.objects.filter(email="newuser@example.com").exists())

    def test_create_user_password_mismatch(self):
        response = self.query(
            """
            mutation {
                createUser(
                    password1: "Password123!",
                    password2: "Password321!",
                    fullName: "New User",
                    email: "newuser@example.com"
                ) {
                    status
                    message
                }
            }
            """
        )
        content = response.json()
        self.assertFalse(content["data"]["createUser"]["status"])
        self.assertIn(
            "Passwords do not match", content["data"]["createUser"]["message"]
        )

    @patch("users.auth_mutation.send_confirmation_email")
    def test_resend_verification_email_success(self, mock_send_email):
        mock_send_email.return_value = {"status": True}
        response = self.query(
            """
            mutation {
                resendVerification(email: "testuser@example.com") {
                    status
                    message
                }
            }
            """
        )
        content = response.json()
        self.assertTrue(content["data"]["resendVerification"]["status"])
        self.assertIn(
            "Successfully sent email to testuser@example.com",
            content["data"]["resendVerification"]["message"],
        )

    def test_verify_user_success(self):
        token = jwt.encode(
            {"user": self.user_unverified.email},
            settings.SECRET_KEY,
            algorithm="HS256",
        ).decode("utf-8")
        response = self.query(
            """
            mutation {
                verifyUser(token: "%s") {
                    status
                    message
                }
            }
            """
            % token
        )
        content = response.json()
        print("DEBUG: ", content)  # Debugging response content
        self.assertTrue(content["data"]["verifyUser"]["status"])
        self.assertEqual(
            content["data"]["verifyUser"]["message"], "Verification Successful"
        )
        self.user_unverified.refresh_from_db()
        self.assertTrue(self.user_unverified.is_verified)

    def test_login_user_success(self):
        response = self.query(
            """
            mutation {
                loginUser(
                    email: "testuser@example.com",
                    password: "Password123!",
                    ip: "127.0.0.1"
                ) {
                    status
                    message
                    token
                    user {
                        email
                        fullName
                    }
                }
            }
            """
        )
        content = response.json()
        print("DEBUG: Login User Success Response:", content)  # Debug
        self.assertTrue(content["data"]["loginUser"]["status"])
        self.assertEqual(
            content["data"]["loginUser"]["message"], "You logged in successfully."
        )
        self.assertEqual(
            content["data"]["loginUser"]["user"]["email"], "testuser@example.com"
        )

    def test_login_user_unverified(self):
        response = self.query(
            """
            mutation {
                loginUser(
                    email: "unverified@example.com",
                    password: "Password123!",
                    ip: "127.0.0.1"
                ) {
                    status
                    message
                }
            }
            """
        )
        content = response.json()
        print("DEBUG: Login User Unverified Response:", content)  # Debug
        self.assertFalse(content["data"]["loginUser"]["status"])
        self.assertIn("Your email is not verified", content["data"]["loginUser"]["message"])

    def test_login_user_invalid_credentials(self):
        response = self.query(
            """
            mutation {
                loginUser(
                    email: "testuser@example.com",
                    password: "WrongPassword!",
                    ip: "127.0.0.1"
                ) {
                    status
                    message
                }
            }
            """
        )
        content = response.json()
        self.assertFalse(content["data"]["loginUser"]["status"])
        self.assertIn(
            "Invalid login credentials", content["data"]["loginUser"]["message"]
        )
