from django.conf import settings
from django.db import models


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Volunteer(Account):
    experience_level = models.CharField(max_length=100)


class Caretaker(Account):
    specialization = models.CharField(max_length=100)
