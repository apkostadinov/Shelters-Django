from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^\+359\d{9}$",
    message="Enter a valid phone number in format +359XXXXXXXXX.",
)


def account_image_upload_to(instance, filename):
    return f"accounts/{instance.pk}/{filename}"


class Account(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=13, validators=[phone_validator])
    image = models.ImageField(upload_to=account_image_upload_to, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.image and self.pk is None:
            image = self.image
            self.image = None
            super().save(*args, **kwargs)
            self.image = image
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return f"{settings.MEDIA_URL}defaults/accounts.png"

    def display_title(self):
        raise NotImplementedError("Subclasses must implement display_title().")

    def __str__(self):
        return f'{self.name} ({self.display_title()})'

class Volunteer(Account):
    EXPERIENCE_LEVEL_CHOICES = [
        ("beginner", "Beginner (Tier 1)"),
        ("intermediate", "Intermediate (Tier 2)"),
        ("advanced", "Advanced (Tier 3)"),
    ]

    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVEL_CHOICES,
    )
    user = models.OneToOneField(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="volunteer_profile",
    )
    shelters = models.ManyToManyField(
        "shelters.Shelter",
        blank=True,
        related_name="volunteers",
    )

    def display_title(self):
        return self.get_experience_level_display()


class Caretaker(Account):
    SPECIALIZATION_CHOICES = [
        ("behavior", "Behavior"),
        ("medical", "Medical"),
        ("nutrition", "Nutrition"),
    ]

    specialization = models.CharField(
        max_length=20,
        choices=SPECIALIZATION_CHOICES,
    )
    user = models.OneToOneField(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="caretaker_profile",
    )

    def display_title(self):
        return self.get_specialization_display()
