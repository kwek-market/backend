from django.test import TestCase
from django.contrib.auth import get_user_model


class UserCreationTests(TestCase):
    def test_create_user_success(self):
        response = self.client.post(
            "/graphql",
            data={
                "query": r"""
                    mutation {
                        createUser(password1: "Password123!", password2: "Password123!", fullName: "Test User", email: "testuser@example.com") {
                            status
                            message
                        }
                    }
                """
            },
            content_type="application/json",
        )
        content = response.json()
        print(content, "DEBUG: Full Response Content")
        self.assertNotIn("errors", content, "GraphQL Errors occurred")
        self.assertTrue(content["data"]["createUser"]["status"])
        self.assertEqual(
            content["data"]["createUser"]["message"],
            "Successfully created account for, testuser@example.com",
        )

    def test_create_user_password_mismatch(self):
        response = self.client.post(
            "/graphql",
            data={
                "query": r"""
                    mutation {
                        createUser(password1: "Password123!", password2: "Password321!", fullName: "Test User", email: "testuser@example.com") {
                            status
                            message
                        }
                    }
                """
            },
            content_type="application/json",
        )
        content = response.json()
        print(content, "DEBUG: Full Response Content")
        self.assertNotIn("errors", content, "GraphQL Errors occurred")
        self.assertFalse(content["data"]["createUser"]["status"])
        self.assertIn(
            "Passwords do not match", content["data"]["createUser"]["message"]
        )

    def test_create_user_duplicate_email(self):
        get_user_model().objects.create_user(
            username="duplicate@example.com",
            email="duplicate@example.com",
            password="Password123!",
        )
        response = self.client.post(
            "/graphql",
            data={
                "query": r"""
                    mutation {
                        createUser(password1: "Password123!", password2: "Password123!", fullName: "Test User", email: "duplicate@example.com") {
                            status
                            message
                        }
                    }
                """
            },
            content_type="application/json",
        )
        content = response.json()
        print(content, "DEBUG: Full Response Content")
        self.assertNotIn("errors", content, "GraphQL Errors occurred")
        self.assertFalse(content["data"]["createUser"]["status"])
        self.assertIn("Email already exists", content["data"]["createUser"]["message"])

    def test_create_user_invalid_email_format(self):
        response = self.client.post(
            "/graphql",
            data={
                "query": r"""
                    mutation {
                        createUser(password1: "Password123!", password2: "Password123!", fullName: "Test User", email: "invalid-email") {
                            status
                            message
                        }
                    }
                """
            },
            content_type="application/json",
        )
        content = response.json()
        print(content, "DEBUG: Full Response Content")
        self.assertNotIn("errors", content, "GraphQL Errors occurred")
        self.assertFalse(content["data"]["createUser"]["status"])
        self.assertIn("Invalid email format", content["data"]["createUser"]["message"])
