from django.conf import settings
from django.db import models


def pet_image_upload_to(instance, filename):
    return f"pets/{instance.pk}/{filename}"


class Pet(models.Model):
    SPECIES_CHOICES = [
        ("dog", "Dog"),
        ("cat", "Cat"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    age = models.PositiveIntegerField()
    description = models.TextField()
    available_for_volunteers = models.BooleanField(default=False)
    available_for_adoption = models.BooleanField(
        default=False,
    )
    image = models.ImageField(upload_to=pet_image_upload_to, blank=True)
    shelter = models.ForeignKey("shelters.Shelter", on_delete=models.CASCADE)
    caretakers = models.ManyToManyField("accounts.Caretaker", blank=True)

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
        return f"{settings.MEDIA_URL}defaults/pets.png"


class Booking(models.Model):
    ACTIVITY_CHOICES = [
        ("walk", "Walk"),
        ("play", "Play"),
        ("training", "Training"),
    ]

    volunteer = models.ForeignKey("accounts.Volunteer", on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    duration = models.DurationField()
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    description = models.TextField(
        null=True,
        blank=True
    )
