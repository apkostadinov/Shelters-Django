from django.db import migrations

PETS = [
    {
        "name": "Buddy",
        "species": "dog",
        "age": 3,
        "description": "Friendly and energetic.",
        "available_for_volunteers": True,
        "available_for_adoption": True,
        "active": True,
        "shelter": "North Ridge Shelter",
    },
    {
        "name": "Luna",
        "species": "cat",
        "age": 2,
        "description": "Calm and affectionate.",
        "available_for_volunteers": True,
        "available_for_adoption": True,
        "active": True,
        "shelter": "North Ridge Shelter",
    },
    {
        "name": "Rocky",
        "species": "dog",
        "age": 5,
        "description": "Loves long walks and outdoor play.",
        "available_for_volunteers": True,
        "available_for_adoption": False,
        "active": True,
        "shelter": "North Ridge Shelter",
    },
    {
        "name": "Bella",
        "species": "cat",
        "age": 4,
        "description": "Shy at first, but very sweet.",
        "available_for_volunteers": True,
        "available_for_adoption": True,
        "active": True,
        "shelter": "Riverbend Rescue",
    },
    {
        "name": "Charlie",
        "species": "dog",
        "age": 6,
        "description": "Gentle and great with people.",
        "available_for_volunteers": False,
        "available_for_adoption": True,
        "active": True,
        "shelter": "Riverbend Rescue",
    },
    {
        "name": "Milo",
        "species": "other",
        "age": 1,
        "description": "Curious and playful companion.",
        "available_for_volunteers": True,
        "available_for_adoption": False,
        "active": True,
        "shelter": "Riverbend Rescue",
    },
    {
        "name": "Daisy",
        "species": "dog",
        "age": 2,
        "description": "Happy and social.",
        "available_for_volunteers": True,
        "available_for_adoption": True,
        "active": True,
        "shelter": "Pine Hollow Haven",
    },
    {
        "name": "Nala",
        "species": "cat",
        "age": 3,
        "description": "Loves quiet corners and treats.",
        "available_for_volunteers": False,
        "available_for_adoption": True,
        "active": True,
        "shelter": "Pine Hollow Haven",
    },
    {
        "name": "Leo",
        "species": "dog",
        "age": 7,
        "description": "Loyal and easygoing.",
        "available_for_volunteers": True,
        "available_for_adoption": False,
        "active": True,
        "shelter": "Pine Hollow Haven",
    },
]


def seed_pets(apps, schema_editor):
    Shelter = apps.get_model("shelters", "Shelter")
    Pet = apps.get_model("pets", "Pet")
    Caretaker = apps.get_model("accounts", "Caretaker")

    shelters_by_name = {
        shelter.name: shelter
        for shelter in Shelter.objects.filter(
            name__in=[
                "North Ridge Shelter",
                "Riverbend Rescue",
                "Pine Hollow Haven",
            ]
        )
    }

    for pet_data in PETS:
        shelter_name = pet_data["shelter"]
        shelter = shelters_by_name.get(shelter_name)
        if shelter is None:
            continue

        pet_defaults = {
            "species": pet_data["species"],
            "age": pet_data["age"],
            "description": pet_data["description"],
            "available_for_volunteers": pet_data["available_for_volunteers"],
            "available_for_adoption": pet_data["available_for_adoption"],
            "active": pet_data["active"],
            "shelter": shelter,
        }
        pet, _ = Pet.objects.update_or_create(
            name=pet_data["name"],
            shelter=shelter,
            defaults=pet_defaults,
        )

        caretakers = list(
            Caretaker.objects.filter(active=True, shelters=shelter).order_by("id")[:2]
        )
        if caretakers:
            pet.caretakers.set(caretakers)


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0002_seed_shelters_caretakers_volunteers"),
    ]

    operations = [
        migrations.RunPython(seed_pets, migrations.RunPython.noop),
    ]
