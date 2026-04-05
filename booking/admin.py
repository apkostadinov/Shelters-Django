from django.contrib import admin
from django import forms

from accounts.models import Caretaker
from pets.models import Pet
from .models import Booking, FeedingTask
from .tasks import send_feeding_task_assignment_email


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("pet", "requested_by", "scheduled_for", "status")
    list_filter = ("status", "scheduled_for")
    search_fields = ("pet__name", "requested_by__username", "requested_by__email")


@admin.register(FeedingTask)
class FeedingTaskAdmin(admin.ModelAdmin):
    class FeedingTaskAdminForm(forms.ModelForm):
        class Meta:
            model = FeedingTask
            fields = "__all__"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            caretaker_field = self.fields.get("caretaker")
            if not caretaker_field:
                return

            pet_id = self.data.get("pet") or getattr(self.instance, "pet_id", None)
            if not pet_id:
                caretaker_field.queryset = Caretaker.objects.filter(active=True).order_by("name")
                return

            shelter_id = (
                Pet.objects.filter(pk=pet_id).values_list("shelter_id", flat=True).first()
            )
            if shelter_id:
                caretaker_field.queryset = (
                    Caretaker.objects.filter(active=True, shelters__id=shelter_id)
                    .distinct()
                    .order_by("name")
                )
            else:
                caretaker_field.queryset = Caretaker.objects.none()

    form = FeedingTaskAdminForm
    list_display = ("pet", "caretaker", "requested_by", "scheduled_for", "status")
    list_filter = ("status", "scheduled_for")
    search_fields = ("pet__name", "caretaker__name")

    def save_model(self, request, obj, form, change):
        previous_caretaker_id = None
        if change and obj.pk:
            previous_caretaker_id = (
                FeedingTask.objects.filter(pk=obj.pk).values_list("caretaker_id", flat=True).first()
            )

        super().save_model(request, obj, form, change)

        new_caretaker_id = obj.caretaker_id
        if not new_caretaker_id:
            return

        if not change:
            event = "assigned"
        elif previous_caretaker_id != new_caretaker_id:
            event = "reassigned"
        else:
            return

        actor_username = request.user.get_username() if request.user.is_authenticated else "admin"
        send_feeding_task_assignment_email.delay(obj.pk, actor_username, event)
