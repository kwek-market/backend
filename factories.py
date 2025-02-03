# factories.py
import factory
from faker import Faker
from django.utils import timezone
from datetime import timedelta
import uuid
from typing import List
import random
from bill.models import *
fake = Faker()


def generate_users(batch_size: int = 10000) -> List[ExtendUser]:
    users = []
    for _ in range(batch_size):
        users.append(
            ExtendUser(email=fake.email(), password=make_password("password123"))
        )
    return ExtendUser.objects.bulk_create(users)


def generate_billings(
    users: List[ExtendUser], batch_size: int = 10000
) -> List[Billing]:
    billings = []
    for user in users:
        for _ in range(random.randint(1, 3)):
            billings.append(
                Billing(
                    id=uuid.uuid4(),
                    full_name=fake.name(),
                    contact=fake.phone_number()[:15],
                    address=fake.street_address(),
                    state=fake.state(),
                    city=fake.city(),
                    user=user,
                )
            )
    return Billing.objects.bulk_create(billings)


def generate_payments(batch_size: int = 10000) -> List[Payment]:
    payments = []
    for _ in range(batch_size):
        payments.append(
            Payment(
                id=uuid.uuid4(),
                amount=random.uniform(10, 1000),
                email=fake.email(),
                name=fake.name(),
                phone=fake.phone_number()[:15],
                verified=random.choice([True, False]),
                used=random.choice([True, False]),
            )
        )
    return Payment.objects.bulk_create(payments)


def generate_coupons(batch_size: int = 1000) -> List[Coupon]:
    coupons = []
    for _ in range(batch_size):
        coupons.append(
            Coupon(
                id=uuid.uuid4(),
                value=random.randint(5, 50),
                valid_until=timezone.now() + timedelta(days=random.randint(1, 365)),
                user_list=[fake.email() for _ in range(random.randint(1, 5))],
            )
        )
    return Coupon.objects.bulk_create(coupons)