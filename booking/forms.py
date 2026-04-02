from django import forms

from accounts.models import Caretaker
from pets.models import Pet
from .models import Booking, FeedingTask
from .permissions import can_manage_booking, can_manage_feeding_tasks


class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["pet", "scheduled_for", "status", "notes"]
        labels = {
            "pet": "Pet",
            "scheduled_for": "Scheduled for",
            "status": "Status",
            "notes": "Notes",
        }
        widgets = {
            "scheduled_for": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional details."}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        user_can_manage = can_manage_booking(self.user)
        pets_queryset = Pet.objects.filter(active=True, shelter__active=True)
        if not user_can_manage:
            pets_queryset = pets_queryset.filter(available_for_volunteers=True)
            self.fields["status"].widget = forms.HiddenInput()
            self.fields["status"].required = False
            self.fields["status"].initial = Booking.Status.PENDING
        self.fields["pet"].queryset = pets_queryset

    def clean(self):
        cleaned_data = super().clean()
        if not can_manage_booking(self.user):
            cleaned_data["status"] = Booking.Status.PENDING
        return cleaned_data

    def save(self, commit=True):
        if not can_manage_booking(self.user):
            self.instance.status = Booking.Status.PENDING
        return super().save(commit=commit)


class BookingEditForm(BookingCreateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not can_manage_booking(self.user):
            self.fields["pet"].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        if not can_manage_booking(self.user) and self.instance.status != Booking.Status.PENDING:
            raise forms.ValidationError("Only pending bookings can be edited.")
        return cleaned_data


class FeedingTaskCreateForm(forms.ModelForm):
    class Meta:
        model = FeedingTask
        fields = ["pet", "caretaker", "scheduled_for", "status", "notes"]
        labels = {
            "pet": "Pet",
            "caretaker": "Caretaker",
            "scheduled_for": "Scheduled for",
            "status": "Status",
            "notes": "Notes",
        }
        widgets = {
            "scheduled_for": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional details."}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["pet"].queryset = Pet.objects.filter(active=True, shelter__active=True)
        self.fields["caretaker"].queryset = Caretaker.objects.filter(active=True).order_by("name")

    def clean(self):
        cleaned_data = super().clean()
        if not can_manage_feeding_tasks(self.user):
            raise forms.ValidationError("You don't have permission to manage feeding tasks.")
        return cleaned_data


class FeedingTaskEditForm(FeedingTaskCreateForm):
    pass
