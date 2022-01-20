from asyncio import FastChildWatcher
import graphene
import jwt

from django.conf import settings

from users.models import ExtendUser

from .models import Message, Notification



class ReadNotification(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=True)
        message_id = graphene.String(required=True)
        notificatin_id = graphene.String(required=True)
    
    @staticmethod
    def mutate(self, info, token, message_id, notification_id):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        if ExtendUser.objects.filter(email=email).exists():
            user = ExtendUser.objects.get(email=email)
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
                        return {
                            "status": False,
                            "message": e
                        }
                else:
                    return {
                        "status": False,
                        "message": "Message does not exist for user"
                    }
            else:
                return {
                    "status": False,
                    "message": "No user notification"
                }
        else:
            return {
                "status": False,
                "message": "Invalid user"
            }
