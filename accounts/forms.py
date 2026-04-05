from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q

from pets.models import Pet
from shelters.models import Shelter
from .models import Caretaker, Volunteer


def _available_volunteer_users(current_user_id=None):
    user_model = get_user_model()
    users = user_model.objects.order_by("username")
    if current_user_id:
        return users.filter(Q(volunteer_profile__isnull=True) | Q(pk=current_user_id))
    return users.filter(volunteer_profile__isnull=True)


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
    username = forms.CharField(
        required=False,
        label="Login username",
        help_text="Optional. If set, a login account will be created for this caretaker.",
        widget=forms.TextInput(attrs={"placeholder": "caretaker_user"}),
    )
    password1 = forms.CharField(
        required=False,
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}),
    )
    password2 = forms.CharField(
        required=False,
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"placeholder": "Repeat password"}),
    )
    assign_caretaker_role = forms.BooleanField(
        required=False,
        initial=True,
        label="Assign caretaker role",
        help_text="Adds user to the CaretakerManager group.",
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
            "phone_number": "Required format: +359 followed by 9 digits.",
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
            "phone_number": forms.TextInput(attrs={"placeholder": "+359888123456"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username", "").strip()
        password1 = cleaned_data.get("password1", "")
        password2 = cleaned_data.get("password2", "")
        email = cleaned_data.get("email", "").strip().lower()

        if username:
            user_model = get_user_model()
            if user_model.objects.filter(username=username).exists():
                self.add_error("username", "This username is already taken.")
            if not password1:
                self.add_error("password1", "Please set a password.")
            if password1 != password2:
                self.add_error("password2", "Passwords do not match.")
            if user_model.objects.filter(email=email).exists():
                self.add_error("email", "A user with this email already exists.")
        elif password1 or password2:
            self.add_error("username", "Provide a username to create a login account.")

        return cleaned_data

    def save(self, commit=True):
        caretaker = super().save(commit=commit)
        if commit:
            shelters = self.cleaned_data["shelters"]
            caretaker.shelters.set(shelters)

            username = self.cleaned_data.get("username", "").strip()
            if username:
                user_model = get_user_model()
                full_name = self.cleaned_data["name"].strip().split(maxsplit=1)
                first_name = full_name[0] if full_name else ""
                last_name = full_name[1] if len(full_name) > 1 else ""
                user = user_model.objects.create_user(
                    username=username,
                    email=self.cleaned_data["email"].strip().lower(),
                    password=self.cleaned_data["password1"],
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=self.cleaned_data["phone_number"],
                )
                user.staffed_shelters.set(shelters)
                if self.cleaned_data.get("assign_caretaker_role"):
                    caretaker_group, _ = Group.objects.get_or_create(name="CaretakerManager")
                    user.groups.add(caretaker_group)
                caretaker.user = user
                caretaker.save(update_fields=["user"])
        return caretaker


class VolunteerCreateForm(forms.ModelForm):
    shelters = forms.ModelMultipleChoiceField(
        queryset=Shelter.objects.filter(active=True).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Shelters",
        help_text="Assign one or more shelters for this volunteer.",
        error_messages={
            "invalid_list": "Select valid shelters.",
        },
    )
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
        label="Linked user account",
        help_text="Optional. Link an existing registered user.",
    )

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
            "phone_number": "Required format: +359 followed by 9 digits.",
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
            "name": forms.TextInput(attrs={"placeholder": "Peter Ivanov"}),
            "email": forms.EmailInput(attrs={"placeholder": "volunteer@example.com"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+359888123456"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = _available_volunteer_users()
        self.fields["user"].label_from_instance = (
            lambda user: f"{user.username} ({user.email})"
        )

    def save(self, commit=True):
        volunteer = super().save(commit=False)
        volunteer.user = self.cleaned_data.get("user")
        if commit:
            volunteer.save()
            volunteer.shelters.set(self.cleaned_data["shelters"])
        return volunteer


class VolunteerEditForm(forms.ModelForm):
    shelters = forms.ModelMultipleChoiceField(
        queryset=Shelter.objects.filter(active=True).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Shelters",
        help_text="Assign one or more shelters for this volunteer.",
        error_messages={
            "invalid_list": "Select valid shelters.",
        },
    )
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
        label="Linked user account",
        help_text="Optional. Link an existing registered user.",
    )

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
            "phone_number": "Required format: +359 followed by 9 digits.",
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
            "name": forms.TextInput(attrs={"placeholder": "Peter Ivanov"}),
            "email": forms.EmailInput(attrs={"placeholder": "volunteer@example.com"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+359888123456"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["shelters"].initial = self.instance.shelters.values_list("id", flat=True)
            current_user_id = self.instance.user_id
        else:
            current_user_id = None
        self.fields["user"].queryset = _available_volunteer_users(current_user_id=current_user_id)
        self.fields["user"].label_from_instance = (
            lambda user: f"{user.username} ({user.email})"
        )
        if self.instance and self.instance.pk:
            self.fields["user"].initial = self.instance.user_id

    def save(self, commit=True):
        volunteer = super().save(commit=False)
        volunteer.user = self.cleaned_data.get("user")
        if commit:
            volunteer.save()
            volunteer.shelters.set(self.cleaned_data["shelters"])
        return volunteer


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
    assign_caretaker_role = forms.BooleanField(
        required=False,
        label="Has caretaker role",
        help_text="For linked login accounts only.",
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
            "phone_number": "Required format: +359 followed by 9 digits.",
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
            "name": forms.TextInput(attrs={"placeholder": "Eva Dobreva"}),
            "email": forms.EmailInput(attrs={"placeholder": "caretaker@example.com"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+359888123456"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["shelters"].initial = self.instance.shelters.values_list("id", flat=True)
            has_role = False
            if self.instance.user_id:
                has_role = self.instance.user.groups.filter(name="CaretakerManager").exists()
            self.fields["assign_caretaker_role"].initial = has_role
        if not self.instance or not self.instance.user_id:
            self.fields["assign_caretaker_role"].disabled = True
            self.fields["assign_caretaker_role"].help_text = "Create a login account first from the create form."

    def save(self, commit=True):
        caretaker = super().save(commit=commit)
        if commit:
            shelters = self.cleaned_data["shelters"]
            caretaker.shelters.set(shelters)
            if caretaker.user_id:
                caretaker.user.staffed_shelters.set(shelters)
                caretaker_group, _ = Group.objects.get_or_create(name="CaretakerManager")
                if self.cleaned_data.get("assign_caretaker_role"):
                    caretaker.user.groups.add(caretaker_group)
                else:
                    caretaker.user.groups.remove(caretaker_group)
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
