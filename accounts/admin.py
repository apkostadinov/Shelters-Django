from django.contrib import admin

from .models import Caretaker, Volunteer


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number", "experience_level", "active")
    list_filter = ("experience_level", "active")
    search_fields = ("name", "email", "phone_number")
    ordering = ("name",)


@admin.register(Caretaker)
class CaretakerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number", "specialization", "active")
    list_filter = ("specialization", "active")
    search_fields = ("name", "email", "phone_number")
    ordering = ("name",)
