from django.db.models.signals import post_save
from django.dispatch import receiver

from pets.models import Pet
from .models import FeedingTask


@receiver(post_save, sender=Pet)
def create_initial_feeding_task(sender, instance, created, **kwargs):
    if not created:
        return
    FeedingTask.objects.create(pet=instance)
