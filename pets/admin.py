from django.contrib import admin

from .models import Pet, PetCaretaker


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "species",
        "age",
        "shelter",
        "available_for_volunteers",
        "available_for_adoption",
        "active",
    )
    list_filter = (
        "species",
        "available_for_volunteers",
        "available_for_adoption",
        "active",
        "shelter",
    )
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(PetCaretaker)
class PetCaretakerAdmin(admin.ModelAdmin):
    list_display = ("pet", "caretaker")
    search_fields = ("pet__name", "caretaker__name")
