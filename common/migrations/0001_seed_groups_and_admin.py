import os

from django.contrib.auth.hashers import make_password
from django.db import migrations

GROUPS = {
    "ShelterAdmin": [
        "add_shelter",
        "change_shelter",
        "delete_shelter",
        "view_shelter",
        "add_pet",
        "change_pet",
        "delete_pet",
        "view_pet",
        "view_booking",
        "add_booking",
        "change_booking",
        "delete_booking",
        "view_feedingtask",
        "add_feedingtask",
        "change_feedingtask",
        "delete_feedingtask",
    ],
    "CaretakerManager": [
        "add_caretaker",
        "change_caretaker",
        "delete_caretaker",
        "view_caretaker",
        "add_volunteer",
        "change_volunteer",
        "delete_volunteer",
        "view_volunteer",
        "view_booking",
        "change_booking",
        "view_feedingtask",
        "change_feedingtask",
    ],
}


def seed_groups_and_admin(apps, schema_editor):
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")
    user_model = apps.get_model("users", "User")

    for group_name, perm_codenames in GROUPS.items():
        group, _ = group_model.objects.get_or_create(name=group_name)
        permissions = permission_model.objects.filter(codename__in=perm_codenames)
        group.permissions.set(permissions)

    username = os.getenv("ADMIN_NAME", "").strip()
    password = os.getenv("ADMIN_PASSWORD", "").strip()
    email = os.getenv("ADMIN_EMAIL", "admin@example.com").strip()
    if not username or not password:
        return

    user, created = user_model.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "is_staff": True,
            "is_superuser": True,
            "password": make_password(password),
        },
    )

    if not created:
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.password = make_password(password)
        user.save(update_fields=["email", "is_staff", "is_superuser", "password"])


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_initial"),
        ("booking", "0003_initial"),
        ("pets", "0002_initial"),
        ("shelters", "0002_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_groups_and_admin, migrations.RunPython.noop),
    ]
