from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Caretaker
from booking.models import Booking, FeedingTask
from pets.models import Pet
from shelters.models import Shelter
from users.models import User


class BookingBaseDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="pass12345",
        )
        cls.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass12345",
        )
        cls.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="pass12345",
        )

        cls.shelter = Shelter.objects.create(
            name="Happy Paws",
            city="Sofia",
            address="1 Main St",
            capacity=50,
        )
        cls.other_shelter = Shelter.objects.create(
            name="Second Home",
            city="Plovdiv",
            address="2 Main St",
            capacity=30,
        )

        cls.pet_public = Pet.objects.create(
            name="Rex",
            species=Pet.AnimalSpecies.DOG,
            age=2,
            description="Friendly dog",
            available_for_volunteers=True,
            shelter=cls.shelter,
        )
        cls.pet_private = Pet.objects.create(
            name="Mimi",
            species=Pet.AnimalSpecies.CAT,
            age=3,
            description="Shy cat",
            available_for_volunteers=False,
            shelter=cls.shelter,
        )

        cls.caretaker_ok = Caretaker.objects.create(
            name="John Care",
            email="care@example.com",
            phone_number="1111111111",
            specialization="nutrition",
        )
        cls.caretaker_ok.shelters.add(cls.shelter)

        cls.caretaker_wrong = Caretaker.objects.create(
            name="Wrong Care",
            email="wrong@example.com",
            phone_number="2222222222",
            specialization="medical",
        )
        cls.caretaker_wrong.shelters.add(cls.other_shelter)

        cls.owner_booking = Booking.objects.create(
            pet=cls.pet_public,
            requested_by=cls.owner,
            scheduled_for=timezone.now() + timedelta(days=1),
            status=Booking.Status.PENDING,
            notes="Owner booking",
        )
        cls.other_booking = Booking.objects.create(
            pet=cls.pet_public,
            requested_by=cls.other_user,
            scheduled_for=timezone.now() + timedelta(days=2),
            status=Booking.Status.PENDING,
            notes="Other booking",
        )

    @staticmethod
    def assign_permissions(user, group_name, codenames):
        group, _ = Group.objects.get_or_create(name=group_name)
        perms = Permission.objects.filter(
            content_type__app_label="booking",
            codename__in=codenames,
        )
        group.permissions.set(perms)
        user.groups.add(group)


class FeedingTaskModelTests(BookingBaseDataMixin, TestCase):
    def test_feeding_task_clean_rejects_caretaker_from_different_shelter(self):
        task = FeedingTask(
            pet=self.pet_public,
            caretaker=self.caretaker_wrong,
            scheduled_for=timezone.now() + timedelta(hours=4),
            status=Booking.Status.PENDING,
        )
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_feeding_task_save_succeeds_for_valid_caretaker(self):
        task = FeedingTask.objects.create(
            pet=self.pet_public,
            caretaker=self.caretaker_ok,
            requested_by=self.owner,
            scheduled_for=timezone.now() + timedelta(hours=2),
            status=Booking.Status.PENDING,
        )
        self.assertEqual(task.caretaker_id, self.caretaker_ok.id)


class BookingCBVAccessTests(BookingBaseDataMixin, TestCase):
    def test_owner_can_view_own_booking_detail(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.get(reverse("booking-detail", kwargs={"pk": self.owner_booking.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_view_foreign_booking_detail(self):
        self.client.login(username="other", password="pass12345")
        response = self.client.get(reverse("booking-detail", kwargs={"pk": self.owner_booking.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_create_booking(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(
            reverse("booking-create-form", kwargs={"shelter_id": self.shelter.id}),
            data={
                "pet": self.pet_public.id,
                "scheduled_for": (timezone.now() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M"),
                "notes": "new booking",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        created = Booking.objects.filter(requested_by=self.owner, notes="new booking").first()
        self.assertIsNotNone(created)
        self.assertEqual(created.status, Booking.Status.PENDING)

    def test_owner_cannot_create_booking_for_private_pet(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(
            reverse("booking-create-form", kwargs={"shelter_id": self.shelter.id}),
            data={
                "pet": self.pet_private.id,
                "scheduled_for": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
                "notes": "blocked",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Booking.objects.filter(requested_by=self.owner, notes="blocked").exists())

    def test_booking_create_step_one_select_shelter_redirects_to_filtered_form(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(
            reverse("booking-create"),
            data={"shelter": self.shelter.id},
        )
        self.assertRedirects(
            response,
            reverse("booking-create-form", kwargs={"shelter_id": self.shelter.id}),
            fetch_redirect_response=False,
        )

    def test_booking_create_form_shows_only_pets_from_selected_shelter(self):
        pet_other_shelter = Pet.objects.create(
            name="OtherShelterPet",
            species=Pet.AnimalSpecies.DOG,
            age=2,
            description="Other shelter pet",
            available_for_volunteers=True,
            shelter=self.other_shelter,
        )

        self.client.login(username="owner", password="pass12345")
        response = self.client.get(reverse("booking-create-form", kwargs={"shelter_id": self.shelter.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        pet_queryset = response.context["form"].fields["pet"].queryset
        self.assertIn(self.pet_public, pet_queryset)
        self.assertNotIn(pet_other_shelter, pet_queryset)

    def test_owner_can_update_pending_booking(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(
            reverse("booking-edit", kwargs={"pk": self.owner_booking.pk}),
            data={
                "scheduled_for": (timezone.now() + timedelta(days=4)).strftime("%Y-%m-%dT%H:%M"),
                "notes": "updated note",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.owner_booking.refresh_from_db()
        self.assertEqual(self.owner_booking.notes, "updated note")

    def test_owner_cannot_update_done_booking(self):
        self.owner_booking.status = Booking.Status.DONE
        self.owner_booking.save()
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(
            reverse("booking-edit", kwargs={"pk": self.owner_booking.pk}),
            data={
                "scheduled_for": (timezone.now() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M"),
                "notes": "should fail",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_pending_booking(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(reverse("booking-delete", kwargs={"pk": self.owner_booking.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(Booking.objects.filter(pk=self.owner_booking.pk).exists())

    def test_owner_cannot_delete_done_booking(self):
        self.owner_booking.status = Booking.Status.DONE
        self.owner_booking.save()
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(reverse("booking-delete", kwargs={"pk": self.owner_booking.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_with_permissions_can_edit_foreign_booking(self):
        self.assign_permissions(
            self.manager,
            "ShelterAdmin",
            ["view_booking", "change_booking"],
        )
        self.client.login(username="manager", password="pass12345")
        response = self.client.post(
            reverse("booking-edit", kwargs={"pk": self.owner_booking.pk}),
            data={
                "pet": self.pet_public.id,
                "scheduled_for": (timezone.now() + timedelta(days=6)).strftime("%Y-%m-%dT%H:%M"),
                "status": Booking.Status.DONE,
                "notes": "manager edit",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.owner_booking.refresh_from_db()
        self.assertEqual(self.owner_booking.status, Booking.Status.DONE)

    def test_manager_without_delete_permission_cannot_delete_booking(self):
        self.assign_permissions(self.manager, "CaretakerManager", ["view_booking", "change_booking"])
        self.client.login(username="manager", password="pass12345")
        response = self.client.post(reverse("booking-delete", kwargs={"pk": self.owner_booking.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("booking.views.send_feeding_task_assignment_email.delay")
    def test_feeding_task_create_queues_assignment_notification(self, mocked_delay):
        self.assign_permissions(
            self.manager,
            "ShelterAdmin",
            ["view_feedingtask", "add_feedingtask", "change_feedingtask"],
        )
        self.client.login(username="manager", password="pass12345")

        response = self.client.post(
            reverse("feeding-task-create"),
            data={
                "pet": self.pet_public.id,
                "caretaker": self.caretaker_ok.id,
                "scheduled_for": (timezone.now() + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M"),
                "status": Booking.Status.PENDING,
                "notes": "feed task",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        created = FeedingTask.objects.order_by("-id").first()
        self.assertIsNotNone(created)
        mocked_delay.assert_called_once_with(
            created.pk,
            self.manager.get_username(),
            "assigned",
        )

    @patch("booking.views.send_feeding_task_assignment_email.delay")
    def test_feeding_task_update_reassign_queues_notification(self, mocked_delay):
        self.assign_permissions(
            self.manager,
            "ShelterAdmin",
            ["view_feedingtask", "change_feedingtask"],
        )
        caretaker_alt = Caretaker.objects.create(
            name="Alt Care",
            email="alt@example.com",
            phone_number="3333333333",
            specialization="behavior",
        )
        caretaker_alt.shelters.add(self.shelter)
        task = FeedingTask.objects.create(
            pet=self.pet_public,
            caretaker=self.caretaker_ok,
            requested_by=self.manager,
            scheduled_for=timezone.now() + timedelta(hours=5),
            status=Booking.Status.PENDING,
            notes="initial",
        )

        self.client.login(username="manager", password="pass12345")
        response = self.client.post(
            reverse("feeding-task-edit", kwargs={"pk": task.pk}),
            data={
                "pet": self.pet_public.id,
                "caretaker": caretaker_alt.id,
                "scheduled_for": (timezone.now() + timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M"),
                "status": Booking.Status.PENDING,
                "notes": "reassigned",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        mocked_delay.assert_called_once_with(
            task.pk,
            self.manager.get_username(),
            "reassigned",
        )


class BookingAPITests(BookingBaseDataMixin, APITestCase):
    def test_unauthenticated_user_cannot_access_booking_api(self):
        response = self.client.get(reverse("api-booking-list-create"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_sees_only_own_bookings_in_api(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.get(reverse("api-booking-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.data}
        self.assertIn(self.owner_booking.id, ids)
        self.assertNotIn(self.other_booking.id, ids)

    def test_manager_with_view_permission_sees_all_bookings_in_api(self):
        self.assign_permissions(self.manager, "ShelterAdmin", ["view_booking"])
        self.client.login(username="manager", password="pass12345")
        response = self.client.get(reverse("api-booking-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.data}
        self.assertIn(self.owner_booking.id, ids)
        self.assertIn(self.other_booking.id, ids)

    def test_regular_user_cannot_set_non_pending_status_on_create(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(
            reverse("api-booking-list-create"),
            data={
                "pet": self.pet_public.id,
                "scheduled_for": (timezone.now() + timedelta(days=1)).isoformat(),
                "status": Booking.Status.DONE,
                "notes": "api booking",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_regular_user_cannot_book_non_volunteer_pet_via_api(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(
            reverse("api-booking-list-create"),
            data={
                "pet": self.pet_private.id,
                "scheduled_for": (timezone.now() + timedelta(days=1)).isoformat(),
                "status": Booking.Status.PENDING,
                "notes": "api blocked",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pet", response.data)

    def test_regular_user_create_sets_requested_by(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(
            reverse("api-booking-list-create"),
            data={
                "pet": self.pet_public.id,
                "scheduled_for": (timezone.now() + timedelta(days=1)).isoformat(),
                "status": Booking.Status.PENDING,
                "notes": "api success",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Booking.objects.get(id=response.data["id"])
        self.assertEqual(created.requested_by_id, self.owner.id)
        self.assertEqual(created.status, Booking.Status.PENDING)
