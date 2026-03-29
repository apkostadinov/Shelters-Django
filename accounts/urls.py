from django.urls import path

from . import views

urlpatterns = [
    path("caretakers/new/", views.CaretakerCreateView.as_view(), name="caretaker-create"),
    path("volunteers/new/", views.VolunteerCreateView.as_view(), name="volunteer-create"),
    path("caretakers/", views.CaretakerListView.as_view(), name="caretaker-list"),
    path("volunteers/", views.VolunteerListView.as_view(), name="volunteer-list"),
    path("caretakers/<int:pk>/", views.CaretakerDetailView.as_view(), name="caretaker-detail"),
    path("volunteers/<int:pk>/", views.VolunteerDetailView.as_view(), name="volunteer-detail"),
    path("caretakers/<int:pk>/edit/", views.CaretakerUpdateView.as_view(), name="caretaker-edit"),
    path("volunteers/<int:pk>/edit/", views.VolunteerUpdateView.as_view(), name="volunteer-edit"),
    path("caretakers/<int:pk>/delete/", views.CaretakerDeleteView.as_view(), name="caretaker-delete"),
    path("volunteers/<int:pk>/delete/", views.VolunteerDeleteView.as_view(), name="volunteer-delete"),
    path(
        "caretakers/<int:pk>/assign-pets/",
        views.CaretakerAssignPetsView.as_view(),
        name="caretaker-assign-pets",
    ),
]
