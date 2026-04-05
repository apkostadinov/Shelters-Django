from celery import shared_task
from django.core.mail import send_mail

from .models import Caretaker
from pets.models import Pet


@shared_task
def send_caretaker_pet_assignment_email(caretaker_id, pet_id):
    try:
        caretaker = Caretaker.objects.select_related("user").get(pk=caretaker_id)
        pet = Pet.objects.select_related("shelter").get(pk=pet_id)
    except (Caretaker.DoesNotExist, Pet.DoesNotExist):
        return

    recipient_email = (
        caretaker.user.email
        if caretaker.user_id and caretaker.user.email
        else caretaker.email
    )
    if not recipient_email:
        return

    subject = f"Pet assigned: {pet.name}"
    message = (
        f"Hello {caretaker.name},\n\n"
        "A pet has been assigned to you.\n"
        f"Pet: {pet.name}\n"
        f"Shelter: {pet.shelter.name}\n"
        f"Species: {pet.get_species_display()}\n"
        f"Age: {pet.age}\n\n"
        "Please check your caretaker dashboard for details.\n\n"
        "Thank you,\n"
        "Pet Shelter"
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[recipient_email],
        fail_silently=False,
    )
