from django import forms

from accounts.models import Caretaker
from .models import Shelter


class ShelterCreateForm(forms.ModelForm):
    class Meta:
        model = Shelter
        fields = [
            "name",
            "city",
            "address",
            "image",
            "capacity",
        ]
        labels = {
            "name": "Shelter name",
            "city": "City",
            "address": "Street address",
            "image": "Shelter photo",
            "capacity": "Capacity",
        }
        help_texts = {
            "name": "Public-facing shelter name.",
            "city": "City where the shelter is located.",
            "address": "Full street address.",
            "image": "Optional. JPG or PNG recommended.",
            "capacity": "Maximum number of pets the shelter can house.",
        }
        error_messages = {
            "name": {"required": "Please enter a shelter name."},
            "city": {"required": "Please enter a city."},
            "address": {"required": "Please enter an address."},
            "capacity": {
                "required": "Please enter the capacity.",
                "invalid": "Capacity must be a whole number.",
            },
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "North Ridge Shelter"}),
            "city": forms.TextInput(attrs={"placeholder": "Austin"}),
            "address": forms.TextInput(attrs={"placeholder": "123 Maple Ave"}),
            "capacity": forms.NumberInput(attrs={"placeholder": "40", "min": "0"}),
        }


class ShelterEditForm(forms.ModelForm):
    class Meta:
        model = Shelter
        fields = [
            "name",
            "city",
            "address",
            "image",
            "capacity",
            "active",
        ]
        labels = {
            "name": "Shelter name",
            "city": "City",
            "address": "Street address",
            "image": "Shelter photo",
            "capacity": "Capacity",
            "active": "Active",
        }
        help_texts = {
            "name": "Public-facing shelter name.",
            "city": "City where the shelter is located.",
            "address": "Full street address.",
            "image": "Optional. JPG or PNG recommended.",
            "capacity": "Maximum number of pets the shelter can house.",
            "active": "Turn off to hide this shelter from public lists.",
        }
        error_messages = {
            "name": {"required": "Please enter a shelter name."},
            "city": {"required": "Please enter a city."},
            "address": {"required": "Please enter an address."},
            "capacity": {
                "required": "Please enter the capacity.",
                "invalid": "Capacity must be a whole number.",
            },
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "North Ridge Shelter"}),
            "city": forms.TextInput(attrs={"placeholder": "Austin"}),
            "address": forms.TextInput(attrs={"placeholder": "123 Maple Ave"}),
            "capacity": forms.NumberInput(attrs={"placeholder": "40", "min": "0"}),
        }


class ShelterCaretakerAssignmentForm(forms.Form):
    caretakers = forms.ModelMultipleChoiceField(
        queryset=Caretaker.objects.filter(active=True).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Assign caretakers",
        help_text="Choose caretakers to assign to this shelter.",
        error_messages={
            "invalid_list": "Select valid caretakers.",
        },
    )

    def __init__(self, *args, **kwargs):
        self.shelter = kwargs.pop("shelter")
        super().__init__(*args, **kwargs)
        self.fields["caretakers"].initial = self.shelter.caretakers.values_list("id", flat=True)

    def save(self):
        caretakers = self.cleaned_data["caretakers"]
        self.shelter.caretakers.set(caretakers)
