from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Caretaker
from .forms import PetCreateForm, PetEditForm
from .models import Pet


def pet_list(request):
    pets = (
        Pet.objects.filter(active=True, shelter__active=True)
        .select_related("shelter")
        .prefetch_related(Prefetch("caretakers", queryset=Caretaker.objects.filter(active=True)))
    )
    return render(request, "pets/list.html", {"pets": pets})


def pet_detail(request, pk):
    pet = get_object_or_404(
        Pet.objects.filter(active=True, shelter__active=True)
        .select_related("shelter")
        .prefetch_related(Prefetch("caretakers", queryset=Caretaker.objects.filter(active=True))),
        pk=pk,
    )
    return render(request, "pets/detail.html", {"pet": pet})


def pet_create(request):
    if request.method == "POST":
        form = PetCreateForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save()
            return redirect("pet-detail", pk=pet.pk)
    else:
        form = PetCreateForm()

    return render(request, "pets/create.html", {"form": form})


def pet_edit(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    if request.method == "POST":
        form = PetEditForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            pet = form.save()
            return redirect("pet-detail", pk=pet.pk)
    else:
        form = PetEditForm(instance=pet)

    return render(request, "pets/edit.html", {"form": form, "pet": pet})


def pet_delete(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    if request.method == "POST":
        pet.delete()
        return redirect("pet-list")
    return render(request, "pets/confirm_delete.html", {"pet": pet})
