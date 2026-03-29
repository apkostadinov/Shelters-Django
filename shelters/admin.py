from django.contrib import admin

from .models import Shelter, ShelterDashboard


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "capacity", "active")
    list_filter = ("city", "active")
    search_fields = ("name", "city", "address")
    ordering = ("name",)
    filter_horizontal = ("caretakers", "staff_members")


@admin.register(ShelterDashboard)
class ShelterDashboardAdmin(admin.ModelAdmin):
    list_display = ("shelter", "updated_at")
    search_fields = ("shelter__name",)
