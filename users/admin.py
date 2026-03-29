from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("phone_number", "city", "avatar")}),
        ("Shelter Access", {"fields": ("is_shelter_manager", "staffed_shelters")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile", {"fields": ("phone_number", "city", "avatar")}),
        ("Shelter Access", {"fields": ("is_shelter_manager", "staffed_shelters")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    filter_horizontal = ("groups", "user_permissions")
