from __future__ import annotations

import random
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Caretaker
from shelters.models import Shelter
from pets.models import Pet


SHELTER_NAMES = [
    "North Ridge Shelter",
    "Riverbend Rescue",
    "Pine Hollow Haven",
]

CITY_NAMES = [
    "Austin",
    "Denver",
    "Portland",
]

STREET_NAMES = [
    "Maple Ave",
    "Oak St",
    "Cedar Rd",
    "Birch Ln",
    "Elm Dr",
]

CARETAKER_SPECIALTIES = [
    "behavior",
    "medical",
    "nutrition",
]

CARETAKER_NAMES = [
    "Avery Collins",
    "Jordan Blake",
    "Riley Chen",
    "Morgan Patel",
    "Casey Nguyen",
    "Taylor Reed",
    "Jamie Ortiz",
    "Alex Harper",
    "Cameron Diaz",
    "Drew Parker",
    "Quinn Rivera",
    "Rowan Brooks",
]

PET_NAMES = [
    "Buddy",
    "Luna",
    "Max",
    "Bella",
    "Charlie",
    "Daisy",
    "Rocky",
    "Milo",
    "Coco",
    "Lucy",
    "Leo",
    "Nala",
    "Oscar",
    "Ruby",
    "Toby",
]

PET_DESCRIPTIONS = [
    "Friendly and curious.",
    "Calm and affectionate.",
    "High energy and playful.",
    "Shy at first but warms up quickly.",
    "Loves long walks and treats.",
]

SPECIES = ["dog", "cat", "other"]


class Command(BaseCommand):
    help = "Seed demo data: 3 shelters, each with 3 caretakers and 5-10 pets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing shelters, caretakers, and pets before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get("reset"):
            Pet.objects.all().delete()
            Caretaker.objects.all().delete()
            Shelter.objects.all().delete()

        created_shelters = []
        for idx in range(3):
            shelter = Shelter.objects.create(
                name=SHELTER_NAMES[idx],
                city=CITY_NAMES[idx],
                address=f"{100 + idx} {random.choice(STREET_NAMES)}",
                capacity=random.randint(20, 60),
                active=True,
            )
            created_shelters.append(shelter)

            caretakers = []
            for c_idx in range(3):
                caretaker = Caretaker.objects.create(
                    name=CARETAKER_NAMES[(idx * 3 + c_idx) % len(CARETAKER_NAMES)],
                    email=f"caretaker{idx + 1}{c_idx + 1}@example.com",
                    phone_number=f"555-010{idx}{c_idx}",
                    specialization=random.choice(CARETAKER_SPECIALTIES),
                    active=True,
                )
                caretakers.append(caretaker)

            shelter.caretakers.add(*caretakers)

            pet_count = random.randint(5, 10)
            for p_idx in range(pet_count):
                pet = Pet.objects.create(
                    name=random.choice(PET_NAMES),
                    species=random.choice(SPECIES),
                    age=random.randint(1, 14),
                    description=random.choice(PET_DESCRIPTIONS),
                    available_for_volunteers=bool(random.getrandbits(1)),
                    available_for_adoption=bool(random.getrandbits(1)),
                    active=True,
                    shelter=shelter,
                )

                assigned = random.sample(caretakers, k=random.randint(1, len(caretakers)))
                pet.caretakers.add(*assigned)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(created_shelters)} shelters with caretakers and pets."
            )
        )
