from django.test import TestCase
from django.urls import reverse

from pets.models import Pet
from shelters.models import Shelter


class HomePageViewTests(TestCase):
    def test_homepage_returns_active_shelter_and_latest_three_pets(self):
        shelter = Shelter.objects.create(
            name="Active Shelter",
            city="Sofia",
            address="Center",
            capacity=15,
            active=True,
        )
        inactive_shelter = Shelter.objects.create(
            name="Inactive Shelter",
            city="Varna",
            address="Sea",
            capacity=15,
            active=False,
        )

        for index in range(5):
            Pet.objects.create(
                name=f"Pet-{index}",
                species="dog",
                age=2,
                description="desc",
                shelter=shelter,
                active=True,
            )
        Pet.objects.create(
            name="InactiveShelterPet",
            species="cat",
            age=2,
            description="desc",
            shelter=inactive_shelter,
            active=True,
        )

        response = self.client.get(reverse("homepage"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["shelter"], shelter)
        pets = list(response.context["pets"])
        self.assertEqual(len(pets), 3)
        self.assertTrue(all(pet.shelter_id == shelter.id for pet in pets))
        self.assertEqual([pet.id for pet in pets], sorted([pet.id for pet in pets], reverse=True))

    def test_homepage_handles_no_active_shelters(self):
        Shelter.objects.create(
            name="Inactive Shelter",
            city="Varna",
            address="Sea",
            capacity=15,
            active=False,
        )

        response = self.client.get(reverse("homepage"))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["shelter"])
        self.assertEqual(list(response.context["pets"]), [])
