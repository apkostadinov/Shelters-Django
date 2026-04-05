from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from accounts.models import Caretaker
from pets.models import Pet
from shelters.forms import (
    ShelterCaretakerAssignmentForm,
    ShelterCreateForm,
    ShelterDashboardForm,
    ShelterEditForm,
)
from shelters.models import Shelter, ShelterDashboard


class ShelterViewsTests(TestCase):
    def setUp(self):
        self.shelter = Shelter.objects.create(
            name="Main Shelter",
            city="Sofia",
            address="Main St",
            capacity=20,
            active=True,
        )
        self.inactive_shelter = Shelter.objects.create(
            name="Inactive Shelter",
            city="Varna",
            address="Side St",
            capacity=20,
            active=False,
        )

        self.staff_user = get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="TestPass123!",
            is_shelter_manager=False,
        )
        self.manager_user = get_user_model().objects.create_user(
            username="manager",
            email="manager@example.com",
            password="TestPass123!",
            is_shelter_manager=True,
        )
        self.outsider_user = get_user_model().objects.create_user(
            username="outsider",
            email="outsider@example.com",
            password="TestPass123!",
        )

        self.shelter.staff_members.add(self.staff_user, self.manager_user)

    def test_shelter_list_excludes_inactive_shelters(self):
        response = self.client.get(reverse("shelter-list"))

        self.assertEqual(response.status_code, 200)
        shelters = list(response.context["shelters"])
        self.assertIn(self.shelter, shelters)
        self.assertNotIn(self.inactive_shelter, shelters)

    def test_latest_additions_limited_to_four(self):
        for index in range(6):
            Pet.objects.create(
                name=f"Pet-{index}",
                species="dog",
                age=2,
                description="desc",
                shelter=self.shelter,
                active=True,
            )

        response = self.client.get(reverse("shelter-latest-additions", kwargs={"pk": self.shelter.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["pets"]), 4)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("shelter-dashboard", kwargs={"pk": self.shelter.pk}))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_for_non_staff_user_is_forbidden(self):
        self.client.force_login(self.outsider_user)
        response = self.client.get(reverse("shelter-dashboard", kwargs={"pk": self.shelter.pk}))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_for_staff_user_is_accessible_and_created(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("shelter-dashboard", kwargs={"pk": self.shelter.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ShelterDashboard.objects.filter(shelter=self.shelter).exists())

    def test_dashboard_edit_requires_shelter_manager_flag(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("shelter-dashboard-edit", kwargs={"pk": self.shelter.pk}))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_edit_updates_for_manager(self):
        self.client.force_login(self.manager_user)

        response = self.client.post(
            reverse("shelter-dashboard-edit", kwargs={"pk": self.shelter.pk}),
            data={"summary": "Updated summary", "priorities": "Updated priorities"},
        )

        self.assertEqual(response.status_code, 302)
        dashboard = ShelterDashboard.objects.get(shelter=self.shelter)
        self.assertEqual(dashboard.summary, "Updated summary")
        self.assertEqual(dashboard.priorities, "Updated priorities")

    def test_assign_caretakers_requires_change_shelter_permission(self):
        self.client.force_login(self.outsider_user)
        response = self.client.get(reverse("shelter-assign-caretakers", kwargs={"pk": self.shelter.pk}))
        self.assertEqual(response.status_code, 403)

        permission = Permission.objects.get(codename="change_shelter")
        self.outsider_user.user_permissions.add(permission)
        response = self.client.get(reverse("shelter-assign-caretakers", kwargs={"pk": self.shelter.pk}))
        self.assertEqual(response.status_code, 200)


class ShelterFormTests(TestCase):
    def setUp(self):
        self.shelter = Shelter.objects.create(
            name="Main Shelter",
            city="Sofia",
            address="Main St",
            capacity=20,
            active=True,
        )
        self.caretaker_a = Caretaker.objects.create(
            name="Caretaker A",
            email="ca@example.com",
            phone_number="111111",
            specialization="behavior",
            active=True,
        )
        self.caretaker_b = Caretaker.objects.create(
            name="Caretaker B",
            email="cb@example.com",
            phone_number="222222",
            specialization="medical",
            active=False,
        )

    def test_shelter_edit_form_city_field_is_disabled(self):
        form = ShelterEditForm(instance=self.shelter)
        self.assertTrue(form.fields["city"].disabled)

    def test_shelter_dashboard_form_prefills_shelter_name(self):
        form = ShelterDashboardForm(shelter=self.shelter)
        self.assertEqual(form.fields["shelter_name"].initial, self.shelter.name)

    def test_shelter_create_form_shows_custom_required_error_for_capacity(self):
        form = ShelterCreateForm(
            data={
                "name": "New Shelter",
                "city": "Sofia",
                "address": "Somewhere",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["capacity"][0], "Please enter the capacity.")

    def test_caretaker_assignment_form_initial_and_save(self):
        self.shelter.caretakers.add(self.caretaker_a)
        form = ShelterCaretakerAssignmentForm(shelter=self.shelter)
        self.assertIn(self.caretaker_a.id, form.fields["caretakers"].initial)

        post_form = ShelterCaretakerAssignmentForm(
            data={"caretakers": [self.caretaker_a.pk]},
            shelter=self.shelter,
        )
        self.assertTrue(post_form.is_valid())
        post_form.save()
        assigned_ids = set(self.shelter.caretakers.values_list("id", flat=True))
        self.assertEqual(assigned_ids, {self.caretaker_a.id})

    def test_caretaker_assignment_form_queryset_contains_only_active(self):
        form = ShelterCaretakerAssignmentForm(shelter=self.shelter)
        caretaker_ids = set(form.fields["caretakers"].queryset.values_list("id", flat=True))

        self.assertIn(self.caretaker_a.id, caretaker_ids)
        self.assertNotIn(self.caretaker_b.id, caretaker_ids)
