from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.core.cache import cache

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
        )
        labels = {
            "username": "Username",
            "email": "Email address",
            "first_name": "First name",
            "last_name": "Last name",
            "phone_number": "Phone number",
            "city": "City",
        }
        help_texts = {
            "username": "Pick a unique username.",
            "email": "We use this for login and notifications.",
            "phone_number": "Optional. Format: +359 followed by 9 digits.",
            "city": "Optional home city.",
        }
        widgets = {
            "phone_number": forms.TextInput(attrs={"placeholder": "+359888123456"}),
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
            "username",
        )
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email address",
            "phone_number": "Phone number",
            "city": "City",
            "username": "Username",
        }
        help_texts = {
            "email": "This is your login email.",
            "phone_number": "Format: +359 followed by 9 digits.",
            "username": "Your username cannot be changed.",
        }
        widgets = {
            "phone_number": forms.TextInput(attrs={"placeholder": "+359888123456"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].disabled = True


class ThrottledPasswordResetForm(PasswordResetForm):
    error_messages = {
        "too_many_attempts": "Too many reset requests. Please try again later.",
    }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not User.objects.filter(email__iexact=email).exists():
            return email

        limit = getattr(settings, "PASSWORD_RESET_EMAIL_LIMIT", 3)
        window_seconds = getattr(settings, "PASSWORD_RESET_EMAIL_WINDOW_SECONDS", 900)
        cache_key = f"password_reset_attempts:{email}"
        attempts = cache.get(cache_key, 0)
        if attempts >= limit:
            raise forms.ValidationError(
                self.error_messages["too_many_attempts"],
                code="too_many_attempts",
            )
        return email

    def save(self, *args, **kwargs):
        email = self.cleaned_data["email"].strip().lower()
        result = super().save(*args, **kwargs)

        if User.objects.filter(email__iexact=email).exists():
            limit = getattr(settings, "PASSWORD_RESET_EMAIL_LIMIT", 3)
            window_seconds = getattr(settings, "PASSWORD_RESET_EMAIL_WINDOW_SECONDS", 900)
            cache_key = f"password_reset_attempts:{email}"
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, timeout=window_seconds)
            if attempts > limit:
                cache.set(cache_key, limit, timeout=window_seconds)

        return result
