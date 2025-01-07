from uuid import UUID
import uuid
import pytest
from django.test import TransactionTestCase
from django.db import connection
from django.test import TestCase

from users.models import ExtendUser, SellerCustomer, SellerProfile


def reset_sequences():
    with connection.cursor() as cursor:
            cursor.execute(
                "TRUNCATE TABLE users_extenduser RESTART IDENTITY CASCADE;"
            )  # Reset primary key sequence

class ExtendUserModelTests(TestCase):
    def setUp(self):
        self.user = ExtendUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            full_name="Test User",
        )

    def test_user_creation(self):
        self.assertIsInstance(self.user.id, UUID)
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.full_name, "Test User")
        self.assertFalse(self.user.is_verified)
        self.assertFalse(self.user.is_seller)

    def test_get_emails_by_ids(self):
        emails = ExtendUser.get_emails_by_ids([self.user.id])
        self.assertIn(self.user.email, emails)

    def test_to_representation(self):
        user_representation = self.user.to_representation()
        self.assertEqual(user_representation["email"], self.user.email)
        self.assertEqual(user_representation["total_spent"], 0)  # Default is 0


class SellerProfileModelTests(TestCase):
    def setUp(self):
        self.user = ExtendUser.objects.create_user(
            username="selleruser",
            email="seller@example.com",
            password="password123",
            full_name="Seller User",
        )
        self.seller_profile = SellerProfile.objects.create(
            user=self.user,
            firstname="Seller",
            lastname="User",
            phone_number="1234567890",
            shop_name="Test Shop",
            shop_url="testshop.com",
            state="Lagos",
            lga="Ikeja",
            landmark="Near Park",
            how_you_heard_about_us="Ads",
            accepted_policy=True,
        )

    def test_seller_profile_creation(self):
        self.assertEqual(self.seller_profile.user, self.user)
        self.assertEqual(self.seller_profile.shop_name, "Test Shop")
        self.assertTrue(self.seller_profile.accepted_policy)

    def test_since_property(self):
        self.assertEqual(self.seller_profile.since, 0)  # Created just now


class SellerCustomerModelTests(TestCase):
    def setUp(self):
        self.user = ExtendUser.objects.create_user(
            username="customeruser",
            email="customer@example.com",
            password="password123",
            full_name="Customer User",
        )
        self.seller_profile = SellerProfile.objects.create(
            user=self.user,
            firstname="Seller",
            lastname="Customer",
            phone_number="1234567890",
            shop_name="Test Customer Shop",
            shop_url="testcustomer.com",
            state="Lagos",
            lga="Ikeja",
            landmark="Near Park",
            how_you_heard_about_us="Referral",
            accepted_policy=True,
        )
        self.seller_customer = SellerCustomer.objects.create(
            seller=self.seller_profile, customer_id=["cust1", "cust2"]
        )

    def test_seller_customer_creation(self):
        self.assertEqual(self.seller_customer.seller, self.seller_profile)
        self.assertIn("cust1", self.seller_customer.customer_id)
        self.assertIn("cust2", self.seller_customer.customer_id)


class BulkOperationTests(TestCase):
    def setUp(self):
        # Creating multiple users
        self.users = [
            ExtendUser(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="password123",
                full_name=f"User {i}",
            )
            for i in range(10)
        ]
        ExtendUser.objects.bulk_create(self.users)

        # Fetching created users to attach to seller profiles
        self.users = ExtendUser.objects.all()
        self.seller_profiles = [
            SellerProfile(
                user=user,
                firstname=f"First{i}",
                lastname=f"Last{i}",
                phone_number=f"123456789{i}",
                shop_name=f"Shop {i}",
                shop_url=f"shop{i}.com",
                state="Lagos",
                lga="Ikeja",
                landmark=f"Landmark {i}",
                how_you_heard_about_us="Referral",
                accepted_policy=True,
            )
            for i, user in enumerate(self.users)
        ]
        SellerProfile.objects.bulk_create(self.seller_profiles)

    def test_bulk_create_users(self):
        self.assertEqual(ExtendUser.objects.count(), 10)
        for i, user in enumerate(ExtendUser.objects.all()):
            self.assertEqual(user.email, f"user{i}@example.com")
            self.assertEqual(user.full_name, f"User {i}")

    def test_bulk_create_seller_profiles(self):
        self.assertEqual(SellerProfile.objects.count(), 10)
        for i, profile in enumerate(SellerProfile.objects.all()):
            self.assertEqual(profile.shop_name, f"Shop {i}")
            self.assertEqual(profile.user.username, f"user{i}")

    def test_bulk_update_users(self):
        # Fetch users and update their `is_verified` field in bulk
        users = ExtendUser.objects.all()
        for user in users:
            user.is_verified = True
        ExtendUser.objects.bulk_update(users, ["is_verified"])

        # Assert all users are marked as verified
        verified_users = ExtendUser.objects.filter(is_verified=True)
        self.assertEqual(verified_users.count(), 10)

    def test_bulk_delete_seller_profiles(self):
        # Bulk delete seller profiles
        SellerProfile.objects.all().delete()
        self.assertEqual(SellerProfile.objects.count(), 0)


# @pytest.mark.django_db
# class TestBulkOperationPerformance(TransactionTestCase):
#     def test_bulk_create_users_performance(self, benchmark):
#         # Clear existing records
#         ExtendUser.objects.all().delete()

#         # Create users with unique emails
#         users = [
#             ExtendUser(
#                 id=uuid.uuid4(),
#                 username=f"user{i}",
#                 email=f"user{i}_{uuid.uuid4()}@example.com",  # Ensure unique emails
#                 password="password123",
#                 full_name=f"User {i}",
#             )
#             for i in range(1000)
#         ]

#         # Benchmark the bulk create operation
#         benchmark(ExtendUser.objects.bulk_create, users)

#     def test_bulk_update_users_performance(self, benchmark):

#         users = [
#             ExtendUser(
#                 username=f"user{i}",
#                 email=f"user{i}@example.com",
#                 password="password123",
#                 full_name=f"User {i}",
#             )
#             for i in range(1000)
#         ]
#         ExtendUser.objects.bulk_create(users)
#         users = list(ExtendUser.objects.all())
#         for user in users:
#             user.is_verified = True
#         benchmark(ExtendUser.objects.bulk_update, users, ["is_verified"])

#     def test_bulk_delete_users_performance(self, benchmark):
#         reset_sequences()  # Reset the sequence
#         users = [
#             ExtendUser(
#                 username=f"user{i}",
#                 email=f"user{i}@example.com",
#                 password="password123",
#                 full_name=f"User {i}",
#             )
#             for i in range(1000)
#         ]
#         ExtendUser.objects.bulk_create(users)
#         benchmark(ExtendUser.objects.all().delete)
