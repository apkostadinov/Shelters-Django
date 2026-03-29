from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView

from pets.models import Pet

from .forms import (
    CaretakerCreateForm,
    CaretakerEditForm,
    PetAssignmentForm,
    VolunteerCreateForm,
    VolunteerEditForm,
)
from .models import Caretaker, Volunteer


class CaretakerListView(ListView):
    model = Caretaker
    template_name = "accounts/caretaker_list.html"
    context_object_name = "caretakers"

    def get_queryset(self):
        return Caretaker.objects.filter(active=True).order_by("name")


class CaretakerDetailView(DetailView):
    model = Caretaker
    template_name = "accounts/caretaker_detail.html"
    context_object_name = "caretaker"

    def get_queryset(self):
        return Caretaker.objects.filter(active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        caretaker = self.object
        context["shelters"] = caretaker.shelters.filter(active=True).order_by("name")
        context["pets"] = (
            Pet.objects.filter(active=True, caretakers=caretaker, shelter__active=True)
            .select_related("shelter")
            .order_by("-created_at", "-id")
        )
        return context


class CaretakerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Caretaker
    form_class = CaretakerCreateForm
    template_name = "accounts/create_caretaker.html"
    permission_required = "accounts.add_caretaker"
    raise_exception = True

    def get_success_url(self):
        return reverse_lazy("caretaker-detail", kwargs={"pk": self.object.pk})


class VolunteerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Volunteer
    form_class = VolunteerCreateForm
    template_name = "accounts/create_volunteer.html"
    permission_required = "accounts.add_volunteer"
    raise_exception = True

    def get_success_url(self):
        return reverse_lazy("volunteer-detail", kwargs={"pk": self.object.pk})


class VolunteerListView(ListView):
    model = Volunteer
    template_name = "accounts/volunteer_list.html"
    context_object_name = "volunteers"

    def get_queryset(self):
        return Volunteer.objects.filter(active=True).order_by("name")


class VolunteerDetailView(DetailView):
    model = Volunteer
    template_name = "accounts/volunteer_detail.html"
    context_object_name = "volunteer"

    def get_queryset(self):
        return Volunteer.objects.filter(active=True)


class CaretakerAssignPetsView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = PetAssignmentForm
    template_name = "accounts/assign_pets.html"
    permission_required = "accounts.change_caretaker"
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        self.caretaker = get_object_or_404(Caretaker.objects.filter(active=True), pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["caretaker"] = self.caretaker
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("caretaker-detail", kwargs={"pk": self.caretaker.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["caretaker"] = self.caretaker
        context["shelters"] = self.caretaker.shelters.filter(active=True).order_by("name")
        return context


class CaretakerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Caretaker
    form_class = CaretakerEditForm
    template_name = "accounts/edit_caretaker.html"
    context_object_name = "caretaker"
    permission_required = "accounts.change_caretaker"
    raise_exception = True

    def get_queryset(self):
        return Caretaker.objects.filter(active=True)

    def get_success_url(self):
        return reverse_lazy("caretaker-detail", kwargs={"pk": self.object.pk})


class CaretakerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Caretaker
    template_name = "accounts/confirm_delete.html"
    context_object_name = "caretaker"
    success_url = reverse_lazy("caretaker-list")
    permission_required = "accounts.delete_caretaker"
    raise_exception = True


class VolunteerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Volunteer
    form_class = VolunteerEditForm
    template_name = "accounts/edit_volunteer.html"
    context_object_name = "volunteer"
    permission_required = "accounts.change_volunteer"
    raise_exception = True

    def get_queryset(self):
        return Volunteer.objects.filter(active=True)

    def get_success_url(self):
        return reverse_lazy("volunteer-detail", kwargs={"pk": self.object.pk})


class VolunteerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Volunteer
    template_name = "accounts/confirm_delete.html"
    context_object_name = "volunteer"
    success_url = reverse_lazy("volunteer-list")
    permission_required = "accounts.delete_volunteer"
    raise_exception = True
