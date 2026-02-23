from django.urls import path

from . import views

urlpatterns = [
    path("caretakers/new/", views.caretaker_create, name="caretaker-create"),
    path("volunteers/new/", views.volunteer_create, name="volunteer-create"),
    path("caretakers/", views.caretaker_list, name="caretaker-list"),
    path("volunteers/", views.volunteer_list, name="volunteer-list"),
    path("caretakers/<int:pk>/", views.caretaker_detail, name="caretaker-detail"),
    path("volunteers/<int:pk>/", views.volunteer_detail, name="volunteer-detail"),
    path("caretakers/<int:pk>/edit/", views.caretaker_edit, name="caretaker-edit"),
    path("volunteers/<int:pk>/edit/", views.volunteer_edit, name="volunteer-edit"),
    path("caretakers/<int:pk>/delete/", views.caretaker_delete, name="caretaker-delete"),
    path("volunteers/<int:pk>/delete/", views.volunteer_delete, name="volunteer-delete"),
    path(
        "caretakers/<int:pk>/assign-pets/",
        views.caretaker_assign_pets,
        name="caretaker-assign-pets",
    ),
]
