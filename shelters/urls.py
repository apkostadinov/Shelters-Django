from django.urls import path

from . import views

urlpatterns = [
    path("", views.ShelterListView.as_view(), name="shelter-list"),
    path("new/", views.ShelterCreateView.as_view(), name="shelter-create"),
    path("<int:pk>/edit/", views.ShelterUpdateView.as_view(), name="shelter-edit"),
    path(
        "<int:pk>/assign-caretakers/",
        views.ShelterAssignCaretakersView.as_view(),
        name="shelter-assign-caretakers",
    ),
    path("<int:pk>/delete/", views.ShelterDeleteView.as_view(), name="shelter-delete"),
    path("<int:pk>/", views.ShelterDetailView.as_view(), name="shelter-detail"),
    path(
        "<int:pk>/latest-additions/",
        views.ShelterLatestAdditionsView.as_view(),
        name="shelter-latest-additions",
    ),
    path("<int:pk>/dashboard/", views.ShelterDashboardDetailView.as_view(), name="shelter-dashboard"),
    path(
        "<int:pk>/dashboard/edit/",
        views.ShelterDashboardUpdateView.as_view(),
        name="shelter-dashboard-edit",
    ),
]
