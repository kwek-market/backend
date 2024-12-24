from django.test import TestCase
from django.contrib.auth import get_user_model


class UserLoginTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="Password123!",
            is_verified=True,
        )
        self.unverified_user = get_user_model().objects.create_user(
            email="unverified@example.com",
            password="Password123!",
            is_verified=False,
        )

    def test_login_user_success(self):
        response = self.client.post(
            "/graphql",
            data={
                "mutation": """
                    mutation {
                        loginUser(email: "testuser@example.com", password: "Password123!") {
                            status
                            message
                        }
                    }
                """
            },
        )
        content = response.json()
        self.assertTrue(content["data"]["loginUser"]["status"])
        self.assertEqual(
            content["data"]["loginUser"]["message"], "You logged in successfully."
        )

    def test_login_user_invalid_credentials(self):
        response = self.client.post(
            "/graphql",
            data={
                "mutation": """
                    mutation {
                        loginUser(email: "testuser@example.com", password: "WrongPassword!") {
                            status
                            message
                        }
                    }
                """
            },
        )
        content = response.json()
        self.assertFalse(content["data"]["loginUser"]["status"])
        self.assertEqual(
            content["data"]["loginUser"]["message"], "Invalid login credentials"
        )

    def test_login_user_unverified_email(self):
        response = self.client.post(
            "/graphql",
            data={
                "mutation": """
                    mutation {
                        loginUser(email: "unverified@example.com", password: "Password123!") {
                            status
                            message
                        }
                    }
                """
            },
        )
        content = response.json()
        self.assertFalse(content["data"]["loginUser"]["status"])
        self.assertEqual(
            content["data"]["loginUser"]["message"], "Your email is not verified"
        )
