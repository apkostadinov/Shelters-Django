from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def pet_image_upload_to(instance, filename):
    return f"pets/{instance.pk}/{filename}"


class Pet(models.Model):
    class AnimalSpecies(models.TextChoices):
        DOG = "dog", "Dog",
        CAT = "cat", "Cat",
        OTHER = "other", "Other"



    name = models.CharField(max_length=100)
    species = models.CharField(
        max_length=20,
        choices=AnimalSpecies
    )
    age = models.PositiveIntegerField()
    description = models.TextField()
    available_for_volunteers = models.BooleanField(default=False)
    available_for_adoption = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to=pet_image_upload_to,
        blank=True
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    shelter = models.ForeignKey(
        "shelters.Shelter",
        on_delete=models.CASCADE
    )
    caretakers = models.ManyToManyField(
        "accounts.Caretaker",
        through="PetCaretaker",
        blank=True,
    )

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

    def __str__(self):
        return f'{self.name}'


# class Booking(models.Model):
#     ACTIVITY_CHOICES = [
#         ("walk", "Walk"),
#         ("play", "Play"),
#         ("training", "Training"),
#     ]
#
#     volunteer = models.ForeignKey("accounts.Volunteer", on_delete=models.CASCADE)
#     pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
#     date = models.DateField()
#     start_time = models.TimeField()
#     duration = models.DurationField()
#     activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
#     description = models.TextField(
#         null=True,
#         blank=True
#     )


class PetCaretaker(models.Model):
    pet = models.ForeignKey("pets.Pet", on_delete=models.CASCADE)
    caretaker = models.ForeignKey("accounts.Caretaker", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["pet", "caretaker"], name="uniq_pet_caretaker"),
        ]

    def clean(self):
        if self.pet_id is None or self.caretaker_id is None:
            return

        allowed = self.pet.shelter_id in self.caretaker.shelters.values_list("id", flat=True)
        if not allowed:
            raise ValidationError(
                "Caretakers can only be assigned to pets in the same shelter."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
