import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification, Message
import time
User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="test@example.com",
        password="password123",
        username="test@example.com",
    )


@pytest.fixture
def notification(user):
    return Notification.objects.create(user=user)


@pytest.fixture
def message(notification):
    return Message.objects.create(
        notification=notification,
        message="Test Message",
        subject="Test Subject",
        read=False,
    )


@pytest.fixture
def valid_token(user):
    import jwt
    from django.conf import settings

    payload = {
        "username": user.email,
        "exp": int(time.time()) + 3600,  # Token valid for 1 hour
        "origIat": int(time.time()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def client():
    from graphene.test import Client
    from users.schema import schema

    return Client(schema)
