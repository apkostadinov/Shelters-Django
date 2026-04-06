from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^\+359\d{9}$",
    message="Enter a valid phone number in format +359XXXXXXXXX.",
)


def user_avatar_upload_to(instance, filename):
    return f"users/{instance.pk}/{filename}"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=13, blank=True, validators=[phone_validator])
    city = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to=user_avatar_upload_to, blank=True)
    is_shelter_manager = models.BooleanField(default=False)

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return f"{settings.MEDIA_URL}{settings.DEFAULT_PROFILE_IMAGE_PATH}"

    def __str__(self):
        return self.get_username()
