from django.urls import path

from .api_views import BookingListCreateAPIView

urlpatterns = [
    path("bookings/", BookingListCreateAPIView.as_view(), name="api-booking-list-create"),
]
