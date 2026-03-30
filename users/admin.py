from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from shelters.models import Shelter
from .models import User


class CustomUserChangeForm(UserChangeForm):
    staffed_shelters = forms.ModelMultipleChoiceField(
        queryset=Shelter.objects.filter(active=True).order_by("name"),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple("Staffed shelters", is_stacked=False),
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["staffed_shelters"].initial = self.instance.staffed_shelters.values_list("pk", flat=True)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.staffed_shelters.set(self.cleaned_data.get("staffed_shelters", []))
        return user


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("phone_number", "city", "avatar")}),
        ("Shelter Access", {"fields": ("is_shelter_manager", "staffed_shelters")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile", {"fields": ("phone_number", "city", "avatar")}),
        ("Shelter Access", {"fields": ("is_shelter_manager",)}),
    )
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    filter_horizontal = ("groups", "user_permissions")
