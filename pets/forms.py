from django import forms

from shelters.models import Shelter
from .models import Pet


class PetCreateForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            "name",
            "species",
            "age",
            "description",
            "available_for_volunteers",
            "available_for_adoption",
            "image",
            "shelter",
        ]
        labels = {
            "name": "Pet name",
            "species": "Species",
            "age": "Age (years)",
            "description": "Description",
            "available_for_volunteers": "Needs volunteers",
            "available_for_adoption": "Available for adoption",
            "image": "Pet photo",
            "shelter": "Shelter",
        }
        help_texts = {
            "name": "Use the pet's public name.",
            "species": "Choose the closest match.",
            "age": "Whole years only.",
            "description": "Short, friendly description for the listing.",
            "image": "Optional. JPG or PNG recommended.",
            "shelter": "Only active shelters are shown.",
        }
        error_messages = {
            "name": {
                "required": "Please enter a pet name.",
                "max_length": "Pet name is too long.",
            },
            "species": {"required": "Please choose a species."},
            "age": {
                "required": "Please provide an age.",
                "invalid": "Age must be a whole number.",
            },
            "description": {"required": "Please add a brief description."},
            "shelter": {"required": "Please select a shelter."},
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Buddy"}),
            "age": forms.NumberInput(attrs={"placeholder": "3", "min": "0"}),
            "description": forms.Textarea(attrs={"placeholder": "Friendly and curious.", "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["shelter"].queryset = Shelter.objects.filter(active=True)


class PetEditForm(PetCreateForm):
    class Meta(PetCreateForm.Meta):
        fields = [
            "name",
            "species",
            "age",
            "description",
            "available_for_volunteers",
            "available_for_adoption",
            "image",
            "shelter",
            "active",
        ]
        labels = {
            **PetCreateForm.Meta.labels,
            "active": "Active listing",
        }
        help_texts = {
            **PetCreateForm.Meta.help_texts,
            "active": "Turn off to hide this pet from public lists.",
        }
