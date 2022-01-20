from graphene_django import DjangoObjectType

from .models import Message, Notification




class MessageType(DjangoObjectType):
    class Meta:
        model = Message


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification