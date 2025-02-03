import pytest
from notifications.models import Notification, Message
import uuid

@pytest.mark.django_db
def test_read_notification_success(client, valid_token, user):
    # Create a notification and message
    notification = Notification.objects.create(user=user)
    message = Message.objects.create(
        notification=notification,
        message="Test Message",
        subject="Test Subject",
        read=False,
    )

    mutation = """
        mutation ReadNotification($token: String!, $messageId: String!, $notificationId: String!) {
            readNotification(token: $token, messageId: $messageId, notificationId: $notificationId) {
                status
                message
            }
        }
    """
    variables = {
        "token": valid_token,
        "messageId": str(message.id),
        "notificationId": str(notification.id),
    }
    response = client.execute(mutation, variables=variables)
    assert response["data"]["readNotification"]["status"] is True
    assert response["data"]["readNotification"]["message"] == "Read Message"
    assert Message.objects.get(id=message.id).read is True


@pytest.mark.django_db
def test_read_notification_invalid_message(client, valid_token, user):
    # Create a notification
    notification = Notification.objects.create(user=user)

    mutation = """
    mutation ReadNotification($token: String!, $messageId: String!, $notificationId: String!) {
        readNotification(token: $token, messageId: $messageId, notificationId: $notificationId) {
            status
            message
        }
    }
    """

    variables = {
        "token": valid_token,
        "messageId": str(uuid.uuid4()),
        "notificationId": str(notification.id),
    }

    # Add authorization header
    client.headers = {"Authorization": f"Bearer {valid_token}"}

    response = client.execute(mutation, variables=variables)

    assert response is not None, "Response should not be None"
    assert "data" in response, "Response should contain 'data' key"
    assert (
        "readNotification" in response["data"]
    ), "Response should contain 'readNotification' key"

    result = response["data"]["readNotification"]
    assert result["status"] is False
    assert "Message does not exist for user" in result["message"]


@pytest.mark.django_db
def test_read_notification_invalid_notification(client, valid_token, user):
    mutation = """
    mutation ReadNotification($token: String!, $messageId: String!, $notificationId: String!) {
        readNotification(token: $token, messageId: $messageId, notificationId: $notificationId) {
            status
            message
        }
    }
    """

    variables = {
        "token": valid_token,
        "messageId": "some_message_id",
        "notificationId": str(uuid.uuid4()),
    }

    # Add authorization header
    client.headers = {"Authorization": f"Bearer {valid_token}"}

    response = client.execute(mutation, variables=variables)

    assert response is not None, "Response should not be None"
    assert "data" in response, "Response should contain 'data' key"
    assert (
        "readNotification" in response["data"]
    ), "Response should contain 'readNotification' key"

    result = response["data"]["readNotification"]
    assert result["status"] is False
    assert "No user notification" in result["message"]
