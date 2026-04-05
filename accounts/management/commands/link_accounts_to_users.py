from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from accounts.models import Caretaker, Volunteer


class Command(BaseCommand):
    help = "Link existing caretaker/volunteer accounts to users by email."

    def add_arguments(self, parser):
        parser.add_argument(
            "--create-missing-users",
            action="store_true",
            help="Create missing users for unlinked accounts when no email match exists.",
        )

    @staticmethod
    def _split_name(full_name):
        parts = (full_name or "").strip().split(maxsplit=1)
        first_name = parts[0] if parts else ""
        last_name = parts[1] if len(parts) > 1 else ""
        return first_name, last_name

    @staticmethod
    def _build_unique_username(user_model, base):
        candidate = slugify(base)[:150] or "user"
        username = candidate
        counter = 1
        while user_model.objects.filter(username=username).exists():
            suffix = f"-{counter}"
            username = f"{candidate[:150 - len(suffix)]}{suffix}"
            counter += 1
        return username

    def _find_or_create_user(self, user_model, email, full_name, create_missing_users):
        try:
            return user_model.objects.get(email__iexact=email), False
        except user_model.DoesNotExist:
            if not create_missing_users:
                return None, False

            first_name, last_name = self._split_name(full_name)
            base_username = email.split("@", 1)[0] if "@" in email else full_name
            username = self._build_unique_username(user_model, base_username)
            user = user_model.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            user.set_unusable_password()
            user.save(update_fields=["password"])
            return user, True
        except user_model.MultipleObjectsReturned:
            user = user_model.objects.filter(email__iexact=email).order_by("id").first()
            return user, False

    def handle(self, *args, **options):
        user_model = get_user_model()
        caretaker_group, _ = Group.objects.get_or_create(name="CaretakerManager")
        create_missing_users = options.get("create_missing_users", False)

        linked_caretakers = 0
        linked_volunteers = 0
        created_users = 0
        skipped = 0

        for caretaker in Caretaker.objects.filter(user__isnull=True):
            email = (caretaker.email or "").strip().lower()
            if not email:
                skipped += 1
                continue

            user, created = self._find_or_create_user(
                user_model=user_model,
                email=email,
                full_name=caretaker.name,
                create_missing_users=create_missing_users,
            )
            if user is None:
                skipped += 1
                continue

            caretaker.user = user
            caretaker.save(update_fields=["user"])
            user.staffed_shelters.set(caretaker.shelters.all())
            user.groups.add(caretaker_group)
            linked_caretakers += 1
            if created:
                created_users += 1

        for volunteer in Volunteer.objects.filter(user__isnull=True):
            email = (volunteer.email or "").strip().lower()
            if not email:
                skipped += 1
                continue

            user, created = self._find_or_create_user(
                user_model=user_model,
                email=email,
                full_name=volunteer.name,
                create_missing_users=create_missing_users,
            )
            if user is None:
                skipped += 1
                continue

            volunteer.user = user
            volunteer.save(update_fields=["user"])
            linked_volunteers += 1
            if created:
                created_users += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Linked caretakers: "
                f"{linked_caretakers}, linked volunteers: {linked_volunteers}, "
                f"created users: {created_users}, skipped: {skipped}."
            )
        )
