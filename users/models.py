from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


def user_avatar_upload_to(instance, filename):
    return f"users/{instance.pk}/{filename}"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to=user_avatar_upload_to, blank=True)

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return f"{settings.MEDIA_URL}defaults/users.png"

    def __str__(self):
        return self.get_username()
