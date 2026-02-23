from django.urls import path

from . import views

urlpatterns = [
    path("", views.shelter_list, name="shelter-list"),
    path("new/", views.shelter_create, name="shelter-create"),
    path("<int:pk>/edit/", views.shelter_edit, name="shelter-edit"),
    path("<int:pk>/assign-caretakers/", views.shelter_assign_caretakers, name="shelter-assign-caretakers"),
    path("<int:pk>/delete/", views.shelter_delete, name="shelter-delete"),
    path("<int:pk>/", views.shelter_detail, name="shelter-detail"),
    path("<int:pk>/latest-additions/", views.shelter_latest_additions, name="shelter-latest-additions"),
]
