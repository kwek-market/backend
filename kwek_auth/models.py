
from django.db import models

# Create your models here.
class Books(models.Model):
    title = models.CharField(max_length=100)
    excerpt = models.TextField()

    def _str_(self):
        return self.title
