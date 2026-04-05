from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from unittest.mock import patch

from shelters.models import Shelter
from users.models import User

from pets.models import Pet
from .models import Caretaker, Volunteer


class VolunteerAccessTests(TestCase):
    def setUp(self):
        self.shelter_a = Shelter.objects.create(
            name="Shelter A",
            city="Sofia",
            address="Address A",
            capacity=20,
            active=True,
        )
        self.shelter_b = Shelter.objects.create(
            name="Shelter B",
            city="Plovdiv",
            address="Address B",
            capacity=25,
            active=True,
        )

        self.allowed_user = User.objects.create_user(
            username="caretaker_user",
            email="caretaker@example.com",
            password="pass12345",
        )
        caretaker_group, _ = Group.objects.get_or_create(name="CaretakerManager")
        self.allowed_user.groups.add(caretaker_group)
        self.allowed_user.staffed_shelters.add(self.shelter_a)

        self.no_shelter_user = User.objects.create_user(
            username="no_shelter_user",
            email="noshelter@example.com",
            password="pass12345",
        )

        self.volunteer_a = Volunteer.objects.create(
            name="Volunteer A",
            email="vola@example.com",
            phone_number="1111111111",
            experience_level="beginner",
            active=True,
        )
        self.volunteer_a.shelters.add(self.shelter_a)

        self.volunteer_b = Volunteer.objects.create(
            name="Volunteer B",
            email="volb@example.com",
            phone_number="2222222222",
            experience_level="advanced",
            active=True,
        )
        self.volunteer_b.shelters.add(self.shelter_b)

    def test_volunteer_list_requires_login(self):
        response = self.client.get(reverse("volunteer-list"))
        self.assertEqual(response.status_code, 302)

    def test_user_without_staffed_shelter_cannot_access_volunteers(self):
        self.client.login(username="no_shelter_user", password="pass12345")
        response = self.client.get(reverse("volunteer-list"))
        self.assertEqual(response.status_code, 403)

    def test_user_sees_only_volunteers_in_their_staffed_shelters(self):
        self.client.login(username="caretaker_user", password="pass12345")
        response = self.client.get(reverse("volunteer-list"))
        self.assertEqual(response.status_code, 200)
        volunteers = list(response.context["volunteers"])
        self.assertIn(self.volunteer_a, volunteers)
        self.assertNotIn(self.volunteer_b, volunteers)

    def test_user_with_shelter_but_without_caretaker_role_cannot_access(self):
        user = User.objects.create_user(
            username="staff_only",
            email="staffonly@example.com",
            password="pass12345",
        )
        user.staffed_shelters.add(self.shelter_a)
        self.client.login(username="staff_only", password="pass12345")
        response = self.client.get(reverse("volunteer-list"))
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_open_foreign_shelter_volunteer_detail(self):
        self.client.login(username="caretaker_user", password="pass12345")
        response = self.client.get(reverse("volunteer-detail", kwargs={"pk": self.volunteer_b.pk}))
        self.assertEqual(response.status_code, 404)


class CaretakerPetAssignmentNotificationTests(TestCase):
    def setUp(self):
        self.shelter = Shelter.objects.create(
            name="Main Shelter",
            city="Sofia",
            address="Address",
            capacity=30,
            active=True,
        )
        self.caretaker = Caretaker.objects.create(
            name="John Care",
            email="care@example.com",
            phone_number="1234567890",
            specialization="behavior",
            active=True,
        )
        self.caretaker.shelters.add(self.shelter)
        self.pet = Pet.objects.create(
            name="Rex",
            species=Pet.AnimalSpecies.DOG,
            age=3,
            description="Friendly",
            shelter=self.shelter,
            active=True,
        )

    @patch("accounts.signals.send_caretaker_pet_assignment_email.delay")
    def test_signal_queues_email_on_caretaker_side_assignment(self, mocked_delay):
        self.caretaker.pet_set.add(self.pet)
        mocked_delay.assert_called_once_with(self.caretaker.pk, self.pet.pk)

    @patch("accounts.signals.send_caretaker_pet_assignment_email.delay")
    def test_signal_queues_email_on_pet_side_assignment(self, mocked_delay):
        self.pet.caretakers.add(self.caretaker)
        mocked_delay.assert_called_once_with(self.caretaker.pk, self.pet.pk)
