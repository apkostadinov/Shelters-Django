from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DONE = "done", "Done"
        MISSED = "missed", "Missed"

    pet = models.ForeignKey(
        "pets.Pet",
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )
    scheduled_for = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Status, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_for", "-id"]

    def __str__(self):
        return f"Booking: {self.pet.name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class FeedingTask(Booking):
    caretaker = models.ForeignKey(
        "accounts.Caretaker",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feeding_tasks",
    )

    class Meta:
        ordering = ["-scheduled_for", "-id"]

    def clean(self):
        if self.caretaker_id is None or self.pet_id is None:
            return
        allowed = self.pet.shelter_id in self.caretaker.shelters.values_list("id", flat=True)
        if not allowed:
            raise ValidationError("Caretaker must belong to the pet's shelter.")

    def __str__(self):
        return f"Feeding: {self.pet.name} ({self.get_status_display()})"
