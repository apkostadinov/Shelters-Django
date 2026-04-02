from rest_framework import serializers

from .models import Booking
from .permissions import can_manage_booking


class BookingSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source="pet.name", read_only=True)
    requested_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "pet",
            "pet_name",
            "requested_by",
            "scheduled_for",
            "status",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "pet_name", "requested_by", "created_at"]

    def validate_pet(self, pet):
        request = self.context["request"]
        if not can_manage_booking(request.user) and not pet.available_for_volunteers:
            raise serializers.ValidationError(
                "This pet is not available for volunteer bookings."
            )
        return pet

    def validate_status(self, status):
        request = self.context["request"]
        if not can_manage_booking(request.user) and status != Booking.Status.PENDING:
            raise serializers.ValidationError(
                "Only managers can set a status other than pending."
            )
        return status

    def create(self, validated_data):
        request = self.context["request"]
        if not can_manage_booking(request.user):
            validated_data["status"] = Booking.Status.PENDING
        validated_data["requested_by"] = request.user
        return super().create(validated_data)
