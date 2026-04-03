from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Compatibility wrapper for legacy command name. Runs seed_groups."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "seed_booking_groups is deprecated. Use seed_groups instead."
            )
        )
        call_command("seed_groups")
