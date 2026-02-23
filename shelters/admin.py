from django.contrib import admin

from .models import Shelter


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "capacity", "active")
    list_filter = ("city", "active")
    search_fields = ("name", "city", "address")
    ordering = ("name",)
