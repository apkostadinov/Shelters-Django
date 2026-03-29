from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "city",
            "avatar",
        )
        labels = {
            "username": "Username",
            "email": "Email address",
            "first_name": "First name",
            "last_name": "Last name",
            "phone_number": "Phone number",
            "city": "City",
            "avatar": "Profile photo",
        }
        help_texts = {
            "username": "Pick a unique username.",
            "email": "We use this for login and notifications.",
            "phone_number": "Optional contact phone.",
            "city": "Optional home city.",
            "avatar": "Optional. JPG or PNG recommended.",
        }
        error_messages = {
            "username": {"required": "Please choose a username."},
            "email": {"required": "Please enter an email address."},
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "city",
            "avatar",
            "username",
        )
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email address",
            "phone_number": "Phone number",
            "city": "City",
            "avatar": "Profile photo",
            "username": "Username",
        }
        help_texts = {
            "email": "This is your login email.",
            "username": "Your username cannot be changed.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].disabled = True
