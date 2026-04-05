from django.db import migrations

SHELTERS = [
    {
        "name": "North Ridge Shelter",
        "city": "Austin",
        "address": "101 Maple Ave",
        "capacity": 45,
        "active": True,
    },
    {
        "name": "Riverbend Rescue",
        "city": "Denver",
        "address": "202 Oak St",
        "capacity": 40,
        "active": True,
    },
    {
        "name": "Pine Hollow Haven",
        "city": "Portland",
        "address": "303 Cedar Rd",
        "capacity": 35,
        "active": True,
    },
]

CARETAKERS = [
    {
        "name": "Avery Collins",
        "email": "caretaker1@example.com",
        "phone_number": "+359888100001",
        "specialization": "behavior",
        "active": True,
        "shelters": ["North Ridge Shelter"],
    },
    {
        "name": "Jordan Blake",
        "email": "caretaker2@example.com",
        "phone_number": "+359888100002",
        "specialization": "medical",
        "active": True,
        "shelters": ["North Ridge Shelter", "Riverbend Rescue"],
    },
    {
        "name": "Riley Chen",
        "email": "caretaker3@example.com",
        "phone_number": "+359888100003",
        "specialization": "nutrition",
        "active": True,
        "shelters": ["Riverbend Rescue"],
    },
    {
        "name": "Morgan Patel",
        "email": "caretaker4@example.com",
        "phone_number": "+359888100004",
        "specialization": "behavior",
        "active": True,
        "shelters": ["Riverbend Rescue", "Pine Hollow Haven"],
    },
    {
        "name": "Casey Nguyen",
        "email": "caretaker5@example.com",
        "phone_number": "+359888100005",
        "specialization": "medical",
        "active": True,
        "shelters": ["Pine Hollow Haven"],
    },
    {
        "name": "Taylor Reed",
        "email": "caretaker6@example.com",
        "phone_number": "+359888100006",
        "specialization": "nutrition",
        "active": True,
        "shelters": ["North Ridge Shelter", "Pine Hollow Haven"],
    },
]

VOLUNTEERS = [
    {
        "name": "Jamie Ortiz",
        "email": "volunteer1@example.com",
        "phone_number": "+359889200001",
        "experience_level": "beginner",
        "active": True,
        "shelters": ["North Ridge Shelter"],
    },
    {
        "name": "Alex Harper",
        "email": "volunteer2@example.com",
        "phone_number": "+359889200002",
        "experience_level": "intermediate",
        "active": True,
        "shelters": ["North Ridge Shelter", "Riverbend Rescue"],
    },
    {
        "name": "Cameron Diaz",
        "email": "volunteer3@example.com",
        "phone_number": "+359889200003",
        "experience_level": "advanced",
        "active": True,
        "shelters": ["Riverbend Rescue"],
    },
    {
        "name": "Drew Parker",
        "email": "volunteer4@example.com",
        "phone_number": "+359889200004",
        "experience_level": "beginner",
        "active": True,
        "shelters": ["Pine Hollow Haven"],
    },
    {
        "name": "Quinn Rivera",
        "email": "volunteer5@example.com",
        "phone_number": "+359889200005",
        "experience_level": "intermediate",
        "active": True,
        "shelters": ["Pine Hollow Haven", "Riverbend Rescue"],
    },
    {
        "name": "Rowan Brooks",
        "email": "volunteer6@example.com",
        "phone_number": "+359889200006",
        "experience_level": "advanced",
        "active": True,
        "shelters": ["North Ridge Shelter"],
    },
]


def seed_shelters_caretakers_volunteers(apps, schema_editor):
    Shelter = apps.get_model("shelters", "Shelter")
    Caretaker = apps.get_model("accounts", "Caretaker")
    Volunteer = apps.get_model("accounts", "Volunteer")

    shelters_by_name = {}
    for shelter_data in SHELTERS:
        shelter, _ = Shelter.objects.update_or_create(
            name=shelter_data["name"],
            defaults={
                "city": shelter_data["city"],
                "address": shelter_data["address"],
                "capacity": shelter_data["capacity"],
                "active": shelter_data["active"],
            },
        )
        shelters_by_name[shelter.name] = shelter

    for caretaker_data in CARETAKERS:
        shelter_names = caretaker_data["shelters"]
        caretaker_defaults = {
            "name": caretaker_data["name"],
            "phone_number": caretaker_data["phone_number"],
            "specialization": caretaker_data["specialization"],
            "active": caretaker_data["active"],
        }
        caretaker, _ = Caretaker.objects.update_or_create(
            email=caretaker_data["email"],
            defaults=caretaker_defaults,
        )
        caretaker.shelters.set(
            [shelters_by_name[name] for name in shelter_names if name in shelters_by_name]
        )

    for volunteer_data in VOLUNTEERS:
        shelter_names = volunteer_data["shelters"]
        volunteer_defaults = {
            "name": volunteer_data["name"],
            "phone_number": volunteer_data["phone_number"],
            "experience_level": volunteer_data["experience_level"],
            "active": volunteer_data["active"],
        }
        volunteer, _ = Volunteer.objects.update_or_create(
            email=volunteer_data["email"],
            defaults=volunteer_defaults,
        )
        volunteer.shelters.set(
            [shelters_by_name[name] for name in shelter_names if name in shelters_by_name]
        )


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0001_seed_groups_and_admin"),
    ]

    operations = [
        migrations.RunPython(seed_shelters_caretakers_volunteers, migrations.RunPython.noop),
    ]
