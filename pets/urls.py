from django.urls import path

from . import views

urlpatterns = [
    path("", views.pet_list, name="pet-list"),
    path("<int:pk>/", views.pet_detail, name="pet-detail"),
]
