from rest_framework import generics

from .api_permissions import CanAccessBookingsAPI
from .models import Booking
from .permissions import can_view_all_bookings
from .serializers import BookingSerializer


class BookingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [CanAccessBookingsAPI]

    def get_queryset(self):
        queryset = Booking.objects.select_related("pet", "requested_by").order_by("-scheduled_for", "-id")
        if can_view_all_bookings(self.request.user):
            return queryset
        return queryset.filter(requested_by=self.request.user)
