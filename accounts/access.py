def can_view_volunteers(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    has_role = user.groups.filter(name="CaretakerManager").exists()
    has_shelters = user.staffed_shelters.filter(active=True).exists()
    return has_role and has_shelters
