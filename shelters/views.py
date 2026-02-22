from django.db.models import Count, F, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render

from pets.models import Pet
from .forms import ShelterCaretakerAssignmentForm, ShelterCreateForm, ShelterEditForm
from .models import Shelter

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


def shelter_latest_additions(request, pk):
    shelter = get_object_or_404(Shelter.objects.filter(active=True), pk=pk)
    latest_pets = _latest_additions_queryset().filter(shelter=shelter)[:LATEST_ADDITIONS_LIMIT]
    return render(
        request,
        "shelters/latest_additions.html",
        {"shelter": shelter, "pets": latest_pets},
    )


def shelter_detail(request, pk):
    shelter = get_object_or_404(
        Shelter.objects.filter(active=True).annotate(
            dog_count=Count("pet", filter=Q(pet__species="dog", pet__active=True)),
            cat_count=Count("pet", filter=Q(pet__species="cat", pet__active=True)),
            other_count=Count("pet", filter=Q(pet__species="other", pet__active=True)),
        ).annotate(
            total_pets=F("dog_count") + F("cat_count") + F("other_count"),
        ),
        pk=pk,
    )
    pets = (
        Pet.objects.filter(shelter=shelter, active=True)
        .order_by("-created_at", "-id")
        .select_related("shelter")
    )
    caretakers = shelter.caretakers.filter(active=True).order_by("name")
    shelter.pet_counts = [
        {"label": "Dog", "count": shelter.dog_count},
        {"label": "Cat", "count": shelter.cat_count},
        {"label": "Other", "count": shelter.other_count},
    ]
    return render(
        request,
        "shelters/detail.html",
        {"shelter": shelter, "pets": pets, "caretakers": caretakers},
    )


def shelter_list(request):
    latest_pets_qs = _latest_additions_queryset()
    shelters = list(
        Shelter.objects.filter(active=True).annotate(
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
    return render(request, "shelters/list.html", {"shelters": shelters})


def shelter_create(request):
    if request.method == "POST":
        form = ShelterCreateForm(request.POST, request.FILES)
        if form.is_valid():
            shelter = form.save()
            return redirect("shelter-detail", pk=shelter.pk)
    else:
        form = ShelterCreateForm()

    return render(request, "shelters/create.html", {"form": form})


def shelter_edit(request, pk):
    shelter = get_object_or_404(Shelter, pk=pk)
    if request.method == "POST":
        form = ShelterEditForm(request.POST, request.FILES, instance=shelter)
        if form.is_valid():
            shelter = form.save()
            return redirect("shelter-detail", pk=shelter.pk)
    else:
        form = ShelterEditForm(instance=shelter)

    return render(request, "shelters/edit.html", {"form": form, "shelter": shelter})


def shelter_delete(request, pk):
    shelter = get_object_or_404(Shelter, pk=pk)
    if request.method == "POST":
        shelter.delete()
        return redirect("shelter-list")
    return render(request, "shelters/confirm_delete.html", {"shelter": shelter})


def shelter_assign_caretakers(request, pk):
    shelter = get_object_or_404(Shelter, pk=pk)
    if request.method == "POST":
        form = ShelterCaretakerAssignmentForm(request.POST, shelter=shelter)
        if form.is_valid():
            form.save()
            return redirect("shelter-detail", pk=shelter.pk)
    else:
        form = ShelterCaretakerAssignmentForm(shelter=shelter)

    return render(
        request,
        "shelters/assign_caretakers.html",
        {"form": form, "shelter": shelter},
    )
