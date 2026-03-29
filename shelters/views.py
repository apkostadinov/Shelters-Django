from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.db.models import Count, F, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView

from pets.models import Pet
from .forms import ShelterCaretakerAssignmentForm, ShelterCreateForm, ShelterDashboardForm, ShelterEditForm
from .models import Shelter, ShelterDashboard

LATEST_ADDITIONS_LIMIT = 4


def _latest_additions_queryset():
    return (
        Pet.objects.filter(active=True)
        .order_by("-created_at", "-id")
        .only(
            "id",
            "name",
            "species",
            "image",
            "shelter_id",
            "created_at",
        )
    )


class ShelterLatestAdditionsView(DetailView):
    model = Shelter
    template_name = "shelters/latest_additions.html"
    context_object_name = "shelter"

    def get_queryset(self):
        return Shelter.objects.filter(active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pets"] = _latest_additions_queryset().filter(
            shelter=self.object
        )[:LATEST_ADDITIONS_LIMIT]
        return context


class ShelterDetailView(DetailView):
    model = Shelter
    template_name = "shelters/detail.html"
    context_object_name = "shelter"

    def get_queryset(self):
        return (
            Shelter.objects.filter(active=True)
            .annotate(
                dog_count=Count("pet", filter=Q(pet__species="dog", pet__active=True)),
                cat_count=Count("pet", filter=Q(pet__species="cat", pet__active=True)),
                other_count=Count("pet", filter=Q(pet__species="other", pet__active=True)),
            )
            .annotate(
                total_pets=F("dog_count") + F("cat_count") + F("other_count"),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shelter = self.object
        context["pets"] = (
            Pet.objects.filter(shelter=shelter, active=True)
            .order_by("-created_at", "-id")
            .select_related("shelter")
        )
        context["caretakers"] = shelter.caretakers.filter(active=True).order_by("name")
        user = self.request.user
        context["can_view_dashboard"] = (
                user.is_authenticated and shelter.staff_members.filter(id=user.id).exists()
        )
        context["can_edit_dashboard"] = context["can_view_dashboard"] and getattr(
            user, "is_shelter_manager", False
        )
        shelter.pet_counts = [
            {"label": "Dog", "count": shelter.dog_count},
            {"label": "Cat", "count": shelter.cat_count},
            {"label": "Other", "count": shelter.other_count},
        ]
        return context


class ShelterListView(ListView):
    model = Shelter
    template_name = "shelters/list.html"
    context_object_name = "shelters"

    def get_queryset(self):
        latest_pets_qs = _latest_additions_queryset()
        shelters = list(
            Shelter.objects.filter(active=True)
            .annotate(
                dog_count=Count("pet", filter=Q(pet__species="dog", pet__active=True)),
                cat_count=Count("pet", filter=Q(pet__species="cat", pet__active=True)),
                other_count=Count("pet", filter=Q(pet__species="other", pet__active=True)),
            )
            .annotate(
                total_pets=F("dog_count") + F("cat_count") + F("other_count"),
            )
            .prefetch_related(
                Prefetch("pet_set", queryset=latest_pets_qs, to_attr="latest_pets"),
            )
            .order_by("name")
        )
        for shelter in shelters:
            shelter.pet_counts = [
                {"label": "Dog", "count": shelter.dog_count},
                {"label": "Cat", "count": shelter.cat_count},
                {"label": "Other", "count": shelter.other_count},
            ]
            shelter.latest_additions = shelter.latest_pets[:LATEST_ADDITIONS_LIMIT]
            user = self.request.user
            shelter.can_view_dashboard = (
                    user.is_authenticated and shelter.staff_members.filter(id=user.id).exists()
            )
        return shelters


class ShelterCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Shelter
    form_class = ShelterCreateForm
    template_name = "shelters/create.html"
    permission_required = "shelters.add_shelter"
    raise_exception = True

    def get_success_url(self):
        return reverse_lazy("shelter-detail", kwargs={"pk": self.object.pk})


class ShelterUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Shelter
    form_class = ShelterEditForm
    template_name = "shelters/edit.html"
    context_object_name = "shelter"
    permission_required = "shelters.change_shelter"
    raise_exception = True

    def get_success_url(self):
        return reverse_lazy("shelter-detail", kwargs={"pk": self.object.pk})


class ShelterDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Shelter
    template_name = "shelters/confirm_delete.html"
    context_object_name = "shelter"
    success_url = reverse_lazy("shelter-list")
    permission_required = "shelters.delete_shelter"
    raise_exception = True


class ShelterAssignCaretakersView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = ShelterCaretakerAssignmentForm
    template_name = "shelters/assign_caretakers.html"
    permission_required = "shelters.change_shelter"
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        self.shelter = get_object_or_404(Shelter, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["shelter"] = self.shelter
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("shelter-detail", kwargs={"pk": self.shelter.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shelter"] = self.shelter
        return context


class ShelterDashboardAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    shelter = None

    def dispatch(self, request, *args, **kwargs):
        self.shelter = get_object_or_404(Shelter.objects.filter(active=True), pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.shelter.staff_members.filter(id=self.request.user.id).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shelter"] = self.shelter
        return context


class ShelterDashboardDetailView(ShelterDashboardAccessMixin, DetailView):
    model = ShelterDashboard
    template_name = "shelters/dashboard_detail.html"
    context_object_name = "dashboard"

    def get_object(self, queryset=None):
        dashboard, _ = ShelterDashboard.objects.get_or_create(shelter=self.shelter)
        return dashboard


class ShelterDashboardUpdateView(ShelterDashboardAccessMixin, UpdateView):
    model = ShelterDashboard
    form_class = ShelterDashboardForm
    template_name = "shelters/dashboard_edit.html"

    def test_func(self):
        return super().test_func() and getattr(self.request.user, "is_shelter_manager", False)

    def get_object(self, queryset=None):
        dashboard, _ = ShelterDashboard.objects.get_or_create(shelter=self.shelter)
        return dashboard

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["shelter"] = self.shelter
        return kwargs

    def get_success_url(self):
        return reverse_lazy("shelter-dashboard", kwargs={"pk": self.shelter.pk})
