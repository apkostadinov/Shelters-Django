from django.urls import path

from . import views

urlpatterns = [
    path("", views.pet_list, name="pet-list"),
    path("new/", views.pet_create, name="pet-create"),
    path("<int:pk>/edit/", views.pet_edit, name="pet-edit"),
    path("<int:pk>/delete/", views.pet_delete, name="pet-delete"),
    path("<int:pk>/", views.pet_detail, name="pet-detail"),
]
