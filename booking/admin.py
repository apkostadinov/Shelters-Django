from django.contrib import admin

from .models import FeedingTask


@admin.register(FeedingTask)
class FeedingTaskAdmin(admin.ModelAdmin):
    list_display = ("pet", "caretaker", "scheduled_for", "status")
    list_filter = ("status", "scheduled_for")
    search_fields = ("pet__name", "caretaker__name")
