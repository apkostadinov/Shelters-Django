from django.apps import AppConfig


class SheltersConfig(AppConfig):
    name = 'shelters'

    def ready(self):
        from . import signals  # noqa: F401
