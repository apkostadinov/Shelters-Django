from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from pets.models import Pet
from .models import Caretaker
from .tasks import send_caretaker_pet_assignment_email


@receiver(m2m_changed, sender=Pet.caretakers.through)
def notify_caretaker_on_pet_assignment(sender, instance, action, reverse, pk_set, **kwargs):
    if action != "post_add" or not pk_set:
        return

    if reverse:
        caretaker = instance
        if not isinstance(caretaker, Caretaker):
            return
        for pet_id in pk_set:
            send_caretaker_pet_assignment_email.delay(caretaker.pk, pet_id)
        return

    pet = instance
    if not isinstance(pet, Pet):
        return
    for caretaker_id in pk_set:
        send_caretaker_pet_assignment_email.delay(caretaker_id, pet.pk)
