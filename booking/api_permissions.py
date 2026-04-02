from rest_framework.permissions import BasePermission


class CanAccessBookingsAPI(BasePermission):
    message = "Authentication is required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
