from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create booking-related groups and assign distinct permissions."

    def handle(self, *args, **options):
        shelter_admin_perms = Permission.objects.filter(
            content_type__app_label="booking",
            codename__in=[
                "view_booking",
                "add_booking",
                "change_booking",
                "delete_booking",
                "view_feedingtask",
                "add_feedingtask",
                "change_feedingtask",
                "delete_feedingtask",
            ],
        )
        caretaker_manager_perms = Permission.objects.filter(
            content_type__app_label="booking",
            codename__in=[
                "view_booking",
                "change_booking",
                "view_feedingtask",
                "change_feedingtask",
            ],
        )

        shelter_admin_group, _ = Group.objects.get_or_create(name="ShelterAdmin")
        shelter_admin_group.permissions.set(shelter_admin_perms)

        caretaker_manager_group, _ = Group.objects.get_or_create(name="CaretakerManager")
        caretaker_manager_group.permissions.set(caretaker_manager_perms)

        self.stdout.write(self.style.SUCCESS("Booking groups and permissions seeded."))
