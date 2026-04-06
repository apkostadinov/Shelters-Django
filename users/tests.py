from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.core.cache import cache

from accounts.models import Volunteer
from users.forms import ThrottledPasswordResetForm, UserProfileForm, UserRegistrationForm
from users.models import User


class UserModelTests(TestCase):
    def test_signup_creates_linked_volunteer_profile(self):
        response = self.client.post(
            reverse("signup"),
            data={
                "username": "newvolunteer",
                "email": "newvolunteer@example.com",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
                "first_name": "New",
                "last_name": "Volunteer",
            },
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username="newvolunteer")
        volunteer = Volunteer.objects.get(user=user)
        self.assertEqual(volunteer.email, "newvolunteer@example.com")
        self.assertEqual(volunteer.name, "New Volunteer")
        self.assertEqual(volunteer.experience_level, "beginner")

    def test_user_forms_do_not_expose_avatar_upload(self):
        registration_form = UserRegistrationForm()
        profile_form = UserProfileForm()

        self.assertNotIn("avatar", registration_form.fields)
        self.assertNotIn("avatar", profile_form.fields)

    @override_settings(
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
        PASSWORD_RESET_EMAIL_LIMIT=2,
        PASSWORD_RESET_EMAIL_WINDOW_SECONDS=300,
    )
    def test_password_reset_form_throttles_registered_email(self):
        user = User.objects.create_user(
            username="throttleuser",
            email="throttle@example.com",
            password="StrongPass123!",
        )
        cache.set(f"password_reset_attempts:{user.email}", 2, timeout=300)

        form = ThrottledPasswordResetForm(data={"email": user.email})

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("Too many reset requests", form.errors["email"][0])

    def test_profile_delete_deletes_current_user_and_redirects(self):
        user = User.objects.create_user(
            username="deleteme",
            email="deleteme@example.com",
            password="StrongPass123!",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("profile-delete"))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=user.pk).exists())
