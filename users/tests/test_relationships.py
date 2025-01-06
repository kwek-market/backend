from django.test import TestCase
from users.models import ExtendUser, SellerProfile, SellerCustomer


class ModelRelationshipTests(TestCase):
    def setUp(self):
        # Create a user instance
        self.user = ExtendUser.objects.create(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            full_name="Test User",
            is_verified=True,
        )

        # Create a seller profile for the user
        self.seller_profile = SellerProfile.objects.create(
            user=self.user,
            firstname="Test",
            lastname="User",
            phone_number="1234567890",
            shop_name="Test Shop",
            shop_url="testshop.com",
            state="Test State",
            lga="Test LGA",
            landmark="Test Landmark",
            how_you_heard_about_us="Referral",
            accepted_policy=True,
        )

        # Create a seller customer associated with the seller profile
        self.seller_customer = SellerCustomer.objects.create(
            seller=self.seller_profile, customer_id=["customer1", "customer2"]
        )

    def test_user_to_seller_profile_relationship(self):
        # Test that a seller profile correctly references its user
        self.assertEqual(self.seller_profile.user, self.user)
        self.assertEqual(self.seller_profile.user.full_name, "Test User")

    def test_seller_profile_to_user_reverse_relationship(self):
        # Test reverse relationship from ExtendUser to SellerProfile
        seller_profile = self.user.seller_profile.first()
        self.assertIsNotNone(seller_profile)
        self.assertEqual(seller_profile.shop_name, "Test Shop")

    def test_seller_profile_to_seller_customer_relationship(self):
        # Test that a seller customer correctly references its seller profile
        self.assertEqual(self.seller_customer.seller, self.seller_profile)
        self.assertListEqual(
            self.seller_customer.customer_id, ["customer1", "customer2"]
        )

    def test_seller_profile_to_seller_customer_reverse_relationship(self):
        # Test reverse relationship from SellerProfile to SellerCustomer
        seller_customer = self.seller_profile.customers
        self.assertEqual(seller_customer.customer_id, ["customer1", "customer2"])

    def test_cascade_delete_user(self):
        # Deleting a user should cascade delete their seller profile and seller customer
        self.user.delete()
        self.assertEqual(SellerProfile.objects.count(), 0)
        self.assertEqual(SellerCustomer.objects.count(), 0)

    def test_cascade_delete_seller_profile(self):
        # Deleting a seller profile should cascade delete its seller customer
        self.seller_profile.delete()
        self.assertEqual(SellerCustomer.objects.count(), 0)

    def test_nullable_relationship(self):
        # Test that SellerProfile.user can be null if allowed
        seller_profile = SellerProfile.objects.create(
            user=None,
            firstname="Orphan",
            lastname="Profile",
            phone_number="1234567899",
            shop_name="Orphan Shop",
            shop_url="orphanshop.com",
            state="Test State",
            lga="Test LGA",
            landmark="Test Landmark",
            how_you_heard_about_us="Ad",
            accepted_policy=True,
        )
        self.assertIsNone(seller_profile.user)

    def test_unique_constraint_on_user_to_seller_profile(self):
        # Test that a user cannot have multiple seller profiles
        with self.assertRaises(
            Exception
        ):  # Replace Exception with IntegrityError if using Django DB exception
            SellerProfile.objects.create(
                user=self.user,
                firstname="Duplicate",
                lastname="Profile",
                phone_number="1234567891",
                shop_name="Duplicate Shop",
                shop_url="duplicateshop.com",
                state="Test State",
                lga="Test LGA",
                landmark="Duplicate Landmark",
                how_you_heard_about_us="Referral",
                accepted_policy=True,
            )
