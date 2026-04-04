from accounts.access import can_view_volunteers


def navigation_flags(request):
    return {
        "can_view_volunteers": can_view_volunteers(request.user),
    }
