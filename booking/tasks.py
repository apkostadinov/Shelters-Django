from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import localtime

from .models import Booking, FeedingTask


@shared_task
def send_booking_notification_email(booking_id, event):
    try:
        booking = Booking.objects.select_related("pet", "requested_by").get(pk=booking_id)
    except Booking.DoesNotExist:
        return

    if not booking.requested_by or not booking.requested_by.email:
        return

    subject = f"Booking {event}: {booking.pet.name}"
    scheduled_for = localtime(booking.scheduled_for).strftime("%Y-%m-%d %H:%M")
    message = (
        f"Hello {booking.requested_by.get_username()},\n\n"
        f"Your booking was {event}.\n"
        f"Pet: {booking.pet.name}\n"
        f"Status: {booking.get_status_display()}\n"
        f"Scheduled for: {scheduled_for}\n\n"
        "Thank you,\n"
        "Pet Shelter"
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[booking.requested_by.email],
        fail_silently=False,
    )


@shared_task
def send_feeding_task_assignment_email(feeding_task_id, actor_username, event):
    try:
        feeding_task = FeedingTask.objects.select_related("pet", "caretaker", "caretaker__user").get(
            pk=feeding_task_id
        )
    except FeedingTask.DoesNotExist:
        return

    if not feeding_task.caretaker:
        return

    recipient_email = (
        feeding_task.caretaker.user.email
        if feeding_task.caretaker.user_id and feeding_task.caretaker.user.email
        else feeding_task.caretaker.email
    )
    if not recipient_email:
        return

    subject = f"Feeding task {event}: {feeding_task.pet.name}"
    scheduled_for = localtime(feeding_task.scheduled_for).strftime("%Y-%m-%d %H:%M")
    message = (
        f"Hello {feeding_task.caretaker.name},\n\n"
        f"A feeding task has been {event} for you.\n"
        f"Pet: {feeding_task.pet.name}\n"
        f"Status: {feeding_task.get_status_display()}\n"
        f"Scheduled for: {scheduled_for}\n"
        f"Assigned by: {actor_username}\n\n"
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
