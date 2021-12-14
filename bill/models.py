import uuid
from django.db import models

from users.models import ExtendUser
# Create your models here.


class Billing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=13)
    address = models.CharField(max_length=355)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    user = models.ForeignKey(ExtendUser, null=True, on_delete=models.CASCADE)


    def __str__(self) -> str:
        return self.first_name

    @property
    def location(self) -> str:
        return f"{self.address} {self.state} {self.city}"


    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Pickups(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=13)
    address = models.CharField(max_length=355)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name
    
    @property
    def location(self) -> str:
        return f"{self.address} {self.state} {self.city}"