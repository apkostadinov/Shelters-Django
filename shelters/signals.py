from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Shelter, ShelterDashboard


@receiver(post_save, sender=Shelter)
def create_dashboard_for_shelter(sender, instance, created, **kwargs):
    if not created:
        return
    ShelterDashboard.objects.create(shelter=instance)
