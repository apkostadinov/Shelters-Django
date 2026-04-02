from django.urls import path

from . import views

urlpatterns = [
    path("", views.BookingListView.as_view(), name="booking-list"),
    path("new/", views.BookingCreateView.as_view(), name="booking-create"),
    path("feeding-tasks/", views.FeedingTaskListView.as_view(), name="feeding-task-list"),
    path("feeding-tasks/new/", views.FeedingTaskCreateView.as_view(), name="feeding-task-create"),
    path("feeding-tasks/<int:pk>/edit/", views.FeedingTaskUpdateView.as_view(), name="feeding-task-edit"),
    path("feeding-tasks/<int:pk>/delete/", views.FeedingTaskDeleteView.as_view(), name="feeding-task-delete"),
    path("feeding-tasks/<int:pk>/", views.FeedingTaskDetailView.as_view(), name="feeding-task-detail"),
    path("<int:pk>/edit/", views.BookingUpdateView.as_view(), name="booking-edit"),
    path("<int:pk>/delete/", views.BookingDeleteView.as_view(), name="booking-delete"),
    path("<int:pk>/", views.BookingDetailView.as_view(), name="booking-detail"),
]
