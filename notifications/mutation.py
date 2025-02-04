import graphene
import jwt

from django.conf import settings

from users.models import ExtendUser
from users.validate import authenticate_user

from .models import Message, Notification


class ReadNotification(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        message_id = graphene.String(required=True)
        notification_id = graphene.String(required=True)

    status = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, token, message_id, notification_id):
        try:
            # Authenticate user
            auth = authenticate_user(token)
            if not auth["status"]:
                return ReadNotification(status=False, message=auth["message"])

            user = auth["user"]

            # Check if notification exists
            try:
                notification = Notification.objects.get(id=notification_id, user=user)
            except Notification.DoesNotExist:
                return ReadNotification(status=False, message="No user notification")

            # Check if message exists
            try:
                message = Message.objects.get(id=message_id, notification=notification)
                message.read = True
                message.save()
                return ReadNotification(status=True, message="Read Message")
            except Message.DoesNotExist:
                return ReadNotification(
                    status=False, message="Message does not exist for user"
                )

        except Exception as e:
            return ReadNotification(status=False, message=str(e))
