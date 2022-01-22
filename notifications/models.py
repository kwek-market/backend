import uuid
from django.db import models
from users.models import ExtendUser

# Create your models here.

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(ExtendUser, on_delete=models.CASCADE, related_name="user")

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="message")
    message = models.TextField(default="")
    subject = models.CharField(max_length=225)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)