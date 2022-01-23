import graphene
import jwt

from django.conf import settings

from users.models import ExtendUser
from users.validate import authenticate_user

from .models import Message, Notification



class ReadNotification(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=True)
        message_id = graphene.String(required=True)
        notification_id = graphene.String(required=True)
    
    @staticmethod
    def mutate(self, info, token, message_id, notification_id):
        auth = authenticate_user(token)
        if not auth["status"]:
            return ReadNotification(status=auth["status"],message=auth["message"])
        user = auth["user"]
        if Notification.objects.filter(id=notification_id, user=user).exists():
            notification = Notification.objects.get(id=notification_id)
            if Message.objects.filter(id=message_id, notification=notification):
                try:
                    Message.objects.filter(id=message_id).update(read=True)
                    return ReadNotification(
                        status=True,
                        message="Read Message"
                    )
                except Exception as e:
                    return ReadNotification(status=False,message=e)
            else:
                return ReadNotification(status=False,message="Message does not exist for user")
        else:
            return ReadNotification(status=False,message="No user notification")
