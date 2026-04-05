from django.test import TestCase
from django.urls import reverse

from accounts.models import Volunteer
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
