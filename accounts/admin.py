from django.contrib import admin
from django import forms

from shelters.models import Shelter
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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["shelters"] = forms.ModelMultipleChoiceField(
            queryset=Shelter.objects.filter(active=True).order_by("name"),
            required=False,
            widget=admin.widgets.FilteredSelectMultiple("Shelters", False),
        )
        if obj and obj.pk:
            form.base_fields["shelters"].initial = obj.shelters.values_list("pk", flat=True)
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.shelters.set(form.cleaned_data.get("shelters", []))
