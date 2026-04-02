from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import (
    BookingCreateForm,
    BookingEditForm,
    FeedingTaskCreateForm,
    FeedingTaskEditForm,
)
from .models import Booking, FeedingTask
from .permissions import (
    can_delete_booking,
    can_delete_feeding_tasks,
    can_manage_booking,
    can_manage_feeding_tasks,
    can_view_all_bookings,
    can_view_feeding_tasks,
)


class BookingAccessMixin(LoginRequiredMixin):
    def get_queryset(self):
        queryset = Booking.objects.select_related("pet", "requested_by").order_by("-scheduled_for", "-id")
        if can_view_all_bookings(self.request.user):
            return queryset
        return queryset.filter(requested_by=self.request.user)


class BookingListView(BookingAccessMixin, ListView):
    model = Booking
    template_name = "booking/list.html"
    context_object_name = "bookings"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_manager"] = can_view_all_bookings(self.request.user)
        context["can_view_feeding_tasks"] = can_view_feeding_tasks(self.request.user)
        return context


class BookingDetailView(BookingAccessMixin, DetailView):
    model = Booking
    template_name = "booking/detail.html"
    context_object_name = "booking"


class BookingCreateView(BookingAccessMixin, CreateView):
    model = Booking
    form_class = BookingCreateForm
    template_name = "booking/create.html"

    def form_valid(self, form):
        form.instance.requested_by = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("booking-detail", kwargs={"pk": self.object.pk})


class BookingUpdateView(BookingAccessMixin, UserPassesTestMixin, UpdateView):
    model = Booking
    form_class = BookingEditForm
    template_name = "booking/edit.html"
    context_object_name = "booking"

    def test_func(self):
        obj = self.get_object()
        if can_manage_booking(self.request.user):
            return True
        return obj.requested_by_id == self.request.user.id and obj.status == Booking.Status.PENDING

    def get_success_url(self):
        return reverse_lazy("booking-detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class BookingDeleteView(BookingAccessMixin, UserPassesTestMixin, DeleteView):
    model = Booking
    template_name = "booking/confirm_delete.html"
    context_object_name = "booking"
    success_url = reverse_lazy("booking-list")

    def test_func(self):
        obj = self.get_object()
        if can_delete_booking(self.request.user):
            return True
        return obj.requested_by_id == self.request.user.id and obj.status == Booking.Status.PENDING


class FeedingTaskAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def get_queryset(self):
        return FeedingTask.objects.select_related("pet", "caretaker", "requested_by").order_by("-scheduled_for", "-id")

    def test_func(self):
        return can_view_feeding_tasks(self.request.user)


class FeedingTaskListView(FeedingTaskAccessMixin, ListView):
    model = FeedingTask
    template_name = "booking/feeding_list.html"
    context_object_name = "feeding_tasks"


class FeedingTaskDetailView(FeedingTaskAccessMixin, DetailView):
    model = FeedingTask
    template_name = "booking/feeding_detail.html"
    context_object_name = "feeding_task"


class FeedingTaskCreateView(FeedingTaskAccessMixin, CreateView):
    model = FeedingTask
    form_class = FeedingTaskCreateForm
    template_name = "booking/feeding_create.html"

    def test_func(self):
        return can_manage_feeding_tasks(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("feeding-task-detail", kwargs={"pk": self.object.pk})


class FeedingTaskUpdateView(FeedingTaskAccessMixin, UpdateView):
    model = FeedingTask
    form_class = FeedingTaskEditForm
    template_name = "booking/feeding_edit.html"
    context_object_name = "feeding_task"

    def test_func(self):
        return can_manage_feeding_tasks(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("feeding-task-detail", kwargs={"pk": self.object.pk})


class FeedingTaskDeleteView(FeedingTaskAccessMixin, DeleteView):
    model = FeedingTask
    template_name = "booking/feeding_confirm_delete.html"
    context_object_name = "feeding_task"
    success_url = reverse_lazy("feeding-task-list")

    def test_func(self):
        return can_delete_feeding_tasks(self.request.user)
