from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from pets.forms import PetCreateForm
from pets.models import Pet
from shelters.models import Shelter


class PetViewsTests(TestCase):
    def setUp(self):
        self.shelter_a = Shelter.objects.create(
            name="Shelter A",
            city="Sofia",
            address="A St",
            capacity=10,
            active=True,
        )
        self.shelter_b = Shelter.objects.create(
            name="Shelter B",
            city="Plovdiv",
            address="B St",
            capacity=10,
            active=True,
        )
        self.inactive_shelter = Shelter.objects.create(
            name="Shelter X",
            city="Varna",
            address="X St",
            capacity=10,
            active=False,
        )

        self.pet_a1 = Pet.objects.create(
            name="Buddy",
            species="dog",
            age=3,
            description="Friendly",
            shelter=self.shelter_a,
            active=True,
        )
        self.pet_a2 = Pet.objects.create(
            name="Luna",
            species="cat",
            age=2,
            description="Calm",
            shelter=self.shelter_a,
            active=True,
        )
        self.inactive_pet = Pet.objects.create(
            name="Hidden",
            species="cat",
            age=4,
            description="Inactive",
            shelter=self.shelter_a,
            active=False,
        )
        self.pet_in_inactive_shelter = Pet.objects.create(
            name="Nope",
            species="dog",
            age=1,
            description="Should be hidden",
            shelter=self.inactive_shelter,
            active=True,
        )

    def test_pet_list_shows_only_active_pets_in_active_shelters(self):
        response = self.client.get(reverse("pet-list"))

        self.assertEqual(response.status_code, 200)
        pets = list(response.context["pets"])
        self.assertIn(self.pet_a1, pets)
        self.assertIn(self.pet_a2, pets)
        self.assertNotIn(self.inactive_pet, pets)
        self.assertNotIn(self.pet_in_inactive_shelter, pets)

    def test_pet_list_filters_by_shelter(self):
        pet_b = Pet.objects.create(
            name="Milo",
            species="dog",
            age=5,
            description="B shelter",
            shelter=self.shelter_b,
            active=True,
        )

        response = self.client.get(reverse("pet-list"), {"shelter": self.shelter_b.pk})
        self.assertEqual(response.status_code, 200)
        pets = list(response.context["pets"])

        self.assertIn(pet_b, pets)
        self.assertNotIn(self.pet_a1, pets)
        self.assertEqual(response.context["selected_shelter"], str(self.shelter_b.pk))

    def test_pet_detail_returns_404_for_inactive_pet(self):
        response = self.client.get(reverse("pet-detail", kwargs={"pk": self.inactive_pet.pk}))
        self.assertEqual(response.status_code, 404)

    def test_pet_create_requires_permission_for_authenticated_user(self):
        user = get_user_model().objects.create_user(
            username="regular",
            email="regular@example.com",
            password="TestPass123!",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("pet-create"))
        self.assertEqual(response.status_code, 403)

    def test_pet_create_with_permission_creates_pet(self):
        user = get_user_model().objects.create_user(
            username="manager",
            email="manager@example.com",
            password="TestPass123!",
        )
        permission = Permission.objects.get(codename="add_pet")
        user.user_permissions.add(permission)
        self.client.force_login(user)

        response = self.client.post(
            reverse("pet-create"),
            data={
                "name": "Rocky",
                "species": "dog",
                "age": 6,
                "description": "Energetic",
                "available_for_volunteers": True,
                "available_for_adoption": False,
                "shelter": self.shelter_a.pk,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Pet.objects.filter(name="Rocky", shelter=self.shelter_a).exists())


class PetFormTests(TestCase):
    def setUp(self):
        self.active_shelter = Shelter.objects.create(
            name="Active Shelter",
            city="Sofia",
            address="Center",
            capacity=10,
            active=True,
        )
        self.inactive_shelter = Shelter.objects.create(
            name="Inactive Shelter",
            city="Varna",
            address="Sea",
            capacity=10,
            active=False,
        )

    def test_pet_create_form_shelter_queryset_contains_only_active_shelters(self):
        form = PetCreateForm()
        shelter_ids = set(form.fields["shelter"].queryset.values_list("id", flat=True))

        self.assertIn(self.active_shelter.id, shelter_ids)
        self.assertNotIn(self.inactive_shelter.id, shelter_ids)

    def test_pet_create_form_shows_custom_required_error_for_name(self):
        form = PetCreateForm(
            data={
                "species": "dog",
                "age": 2,
                "description": "desc",
                "shelter": self.active_shelter.pk,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"][0], "Please enter a pet name.")
