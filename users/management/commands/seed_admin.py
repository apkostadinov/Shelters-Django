from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

import environ


class Command(BaseCommand):
    help = "Create or update a superuser from environment variables."

    def handle(self, *args, **options):
        env = environ.Env()

        username = env("ADMIN_NAME", default="").strip()
        password = env("ADMIN_PASSWORD", default="").strip()
        email = env("ADMIN_EMAIL", default="admin@example.com").strip()

        if not username:
            raise CommandError("ADMIN_NAME is not set.")
        if not password:
            raise CommandError("ADMIN_PASSWORD is not set.")

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if not created:
            user.email = email
            user.is_staff = True
            user.is_superuser = True

        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(f"{action} admin user '{username}'.")
        )
