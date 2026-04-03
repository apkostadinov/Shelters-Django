from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default groups with distinct permissions."

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

    def handle(self, *args, **options):
        for group_name, perm_codenames in self.GROUPS.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            permissions = Permission.objects.filter(codename__in=perm_codenames)
            group.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS(f"Ensured group {group_name}"))
