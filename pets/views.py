from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.models import Caretaker
from shelters.models import Shelter
from .forms import PetCreateForm, PetEditForm
from .models import Pet


class PetListView(ListView):
    model = Pet
    template_name = "pets/list.html"
    context_object_name = "pets"

    def get_queryset(self):
        shelter_id = self.request.GET.get("shelter")
        pets = Pet.objects.filter(active=True, shelter__active=True)
        if shelter_id:
            pets = pets.filter(shelter_id=shelter_id)
        return (
            pets.select_related("shelter")
            .prefetch_related(Prefetch("caretakers", queryset=Caretaker.objects.filter(active=True)))
            .order_by("?")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shelters"] = Shelter.objects.filter(active=True).order_by("name")
        context["selected_shelter"] = self.request.GET.get("shelter")
        return context


class PetDetailView(DetailView):
    model = Pet
    template_name = "pets/detail.html"
    context_object_name = "pet"

    def get_queryset(self):
        return (
            Pet.objects.filter(active=True, shelter__active=True)
            .select_related("shelter")
            .prefetch_related(Prefetch("caretakers", queryset=Caretaker.objects.filter(active=True)))
        )


class PetCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Pet
    form_class = PetCreateForm
    template_name = "pets/create.html"
    permission_required = "pets.add_pet"
    raise_exception = True

    def get_success_url(self):
        return reverse_lazy("pet-detail", kwargs={"pk": self.object.pk})


class PetUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Pet
    form_class = PetEditForm
    template_name = "pets/edit.html"
    context_object_name = "pet"
    permission_required = "pets.change_pet"
    raise_exception = True

    def get_success_url(self):
        return reverse_lazy("pet-detail", kwargs={"pk": self.object.pk})


class PetDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Pet
    template_name = "pets/confirm_delete.html"
    context_object_name = "pet"
    success_url = reverse_lazy("pet-list")
    permission_required = "pets.delete_pet"
    raise_exception = True
