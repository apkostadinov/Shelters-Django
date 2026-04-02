from django.contrib import admin

from .models import Booking, FeedingTask


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("pet", "requested_by", "scheduled_for", "status")
    list_filter = ("status", "scheduled_for")
    search_fields = ("pet__name", "requested_by__username", "requested_by__email")


@admin.register(FeedingTask)
class FeedingTaskAdmin(admin.ModelAdmin):
    list_display = ("pet", "caretaker", "requested_by", "scheduled_for", "status")
    list_filter = ("status", "scheduled_for")
    search_fields = ("pet__name", "caretaker__name")
