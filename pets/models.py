from django.db import models


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
    shelter = models.ForeignKey("shelters.Shelter", on_delete=models.CASCADE)
    caretakers = models.ManyToManyField("accounts.Caretaker", blank=True)


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
