from django.urls import path

from . import views

urlpatterns = [
    path("", views.PetListView.as_view(), name="pet-list"),
    path("new/", views.PetCreateView.as_view(), name="pet-create"),
    path("<int:pk>/edit/", views.PetUpdateView.as_view(), name="pet-edit"),
    path("<int:pk>/delete/", views.PetDeleteView.as_view(), name="pet-delete"),
    path("<int:pk>/", views.PetDetailView.as_view(), name="pet-detail"),
]
