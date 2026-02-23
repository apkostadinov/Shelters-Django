from django import forms

from pets.models import Pet
from shelters.models import Shelter
from .models import Caretaker, Volunteer


class CaretakerCreateForm(forms.ModelForm):
    shelters = forms.ModelMultipleChoiceField(
        queryset=Shelter.objects.filter(active=True).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Shelters",
        help_text="Assign one or more shelters for this caretaker.",
        error_messages={
            "invalid_list": "Select valid shelters.",
        },
    )

    class Meta:
        model = Caretaker
        fields = [
            "name",
            "email",
            "phone_number",
            "image",
            "specialization",
        ]
        labels = {
            "name": "Full name",
            "email": "Email address",
            "phone_number": "Phone number",
            "image": "Profile photo",
            "specialization": "Specialization",
        }
        help_texts = {
            "name": "First and last name preferred.",
            "email": "Used for internal contact.",
            "phone_number": "Include country/area code if possible.",
            "image": "Optional. JPG or PNG recommended.",
            "specialization": "Select the caretaker’s primary focus.",
        }
        error_messages = {
            "name": {"required": "Please enter a name."},
            "email": {
                "required": "Please enter an email address.",
                "invalid": "Enter a valid email address.",
            },
            "phone_number": {"required": "Please enter a phone number."},
            "specialization": {"required": "Please select a specialization."},
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Avery Collins"}),
            "email": forms.EmailInput(attrs={"placeholder": "caretaker@example.com"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "555-0123"}),
        }

    def save(self, commit=True):
        caretaker = super().save(commit=commit)
        if commit:
            caretaker.shelters.set(self.cleaned_data["shelters"])
        return caretaker


class VolunteerCreateForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = [
            "name",
            "email",
            "phone_number",
            "image",
            "experience_level",
        ]
        labels = {
            "name": "Full name",
            "email": "Email address",
            "phone_number": "Phone number",
            "image": "Profile photo",
            "experience_level": "Experience level",
        }
        help_texts = {
            "name": "First and last name preferred.",
            "email": "Used for internal contact.",
            "phone_number": "Include country/area code if possible.",
            "image": "Optional. JPG or PNG recommended.",
            "experience_level": "Choose the level that best fits.",
        }
        error_messages = {
            "name": {"required": "Please enter a name."},
            "email": {
                "required": "Please enter an email address.",
                "invalid": "Enter a valid email address.",
            },
            "phone_number": {"required": "Please enter a phone number."},
            "experience_level": {"required": "Please select an experience level."},
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Jordan Blake"}),
            "email": forms.EmailInput(attrs={"placeholder": "volunteer@example.com"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "555-0456"}),
        }


class VolunteerEditForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = [
            "name",
            "email",
            "phone_number",
            "image",
            "experience_level",
            "active",
        ]
        labels = {
            "name": "Full name",
            "email": "Email address",
            "phone_number": "Phone number",
            "image": "Profile photo",
            "experience_level": "Experience level",
            "active": "Active",
        }
        help_texts = {
            "name": "First and last name preferred.",
            "email": "Used for internal contact.",
            "phone_number": "Include country/area code if possible.",
            "image": "Optional. JPG or PNG recommended.",
            "experience_level": "Choose the level that best fits.",
            "active": "Turn off to hide this volunteer from public lists.",
        }
        error_messages = {
            "name": {"required": "Please enter a name."},
            "email": {
                "required": "Please enter an email address.",
                "invalid": "Enter a valid email address.",
            },
            "phone_number": {"required": "Please enter a phone number."},
            "experience_level": {"required": "Please select an experience level."},
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Jordan Blake"}),
            "email": forms.EmailInput(attrs={"placeholder": "volunteer@example.com"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "555-0456"}),
        }


class CaretakerEditForm(forms.ModelForm):
    shelters = forms.ModelMultipleChoiceField(
        queryset=Shelter.objects.filter(active=True).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Shelters",
        help_text="Assign one or more shelters for this caretaker.",
        error_messages={
            "invalid_list": "Select valid shelters.",
        },
    )

    class Meta:
        model = Caretaker
        fields = [
            "name",
            "email",
            "phone_number",
            "image",
            "specialization",
            "active",
        ]
        labels = {
            "name": "Full name",
            "email": "Email address",
            "phone_number": "Phone number",
            "image": "Profile photo",
            "specialization": "Specialization",
            "active": "Active",
        }
        help_texts = {
            "name": "First and last name preferred.",
            "email": "Used for internal contact.",
            "phone_number": "Include country/area code if possible.",
            "image": "Optional. JPG or PNG recommended.",
            "specialization": "Select the caretaker’s primary focus.",
            "active": "Turn off to hide this caretaker from public lists.",
        }
        error_messages = {
            "name": {"required": "Please enter a name."},
            "email": {
                "required": "Please enter an email address.",
                "invalid": "Enter a valid email address.",
            },
            "phone_number": {"required": "Please enter a phone number."},
            "specialization": {"required": "Please select a specialization."},
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Avery Collins"}),
            "email": forms.EmailInput(attrs={"placeholder": "caretaker@example.com"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "555-0123"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["shelters"].initial = self.instance.shelters.values_list("id", flat=True)

    def save(self, commit=True):
        caretaker = super().save(commit=commit)
        if commit:
            caretaker.shelters.set(self.cleaned_data["shelters"])
        return caretaker


class PetAssignmentForm(forms.Form):
    pets = forms.ModelMultipleChoiceField(
        queryset=Pet.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Assign pets",
        help_text="Only pets from this caretaker’s shelters are available.",
        error_messages={
            "invalid_list": "Select valid pets.",
        },
    )

    def __init__(self, *args, **kwargs):
        self.caretaker = kwargs.pop("caretaker")
        super().__init__(*args, **kwargs)
        self.fields["pets"].queryset = (
            Pet.objects.filter(
                active=True,
                shelter__active=True,
                shelter__in=self.caretaker.shelters.all(),
            )
            .select_related("shelter")
            .order_by("name")
        )
        self.fields["pets"].initial = self.caretaker.pet_set.values_list("id", flat=True)
        self.fields["pets"].label_from_instance = (
            lambda pet: f"{pet.name} · {pet.age} yrs · {pet.shelter.name}"
        )

    def save(self):
        pets = self.cleaned_data["pets"]
        self.caretaker.pet_set.set(pets)
