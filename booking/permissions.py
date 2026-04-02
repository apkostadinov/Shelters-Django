MANAGER_GROUP_NAMES = ("ShelterAdmin", "CaretakerManager")


def is_booking_manager(user):
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name__in=MANAGER_GROUP_NAMES).exists()


def can_view_all_bookings(user):
    return is_booking_manager(user) and user.has_perm("booking.view_booking")


def can_manage_booking(user):
    return is_booking_manager(user) and user.has_perm("booking.change_booking")


def can_delete_booking(user):
    return is_booking_manager(user) and user.has_perm("booking.delete_booking")


def can_view_feeding_tasks(user):
    return is_booking_manager(user) and user.has_perm("booking.view_feedingtask")


def can_manage_feeding_tasks(user):
    return is_booking_manager(user) and user.has_perm("booking.change_feedingtask")


def can_delete_feeding_tasks(user):
    return is_booking_manager(user) and user.has_perm("booking.delete_feedingtask")
