from django.shortcuts import get_object_or_404, redirect, render

from pets.models import Pet

from .forms import CaretakerCreateForm, CaretakerEditForm, PetAssignmentForm, VolunteerCreateForm
from .models import Caretaker


def caretaker_list(request):
    caretakers = Caretaker.objects.filter(active=True).order_by("name")
    return render(request, "accounts/caretaker_list.html", {"caretakers": caretakers})


def caretaker_detail(request, pk):
    caretaker = get_object_or_404(Caretaker.objects.filter(active=True), pk=pk)
    shelters = caretaker.shelters.filter(active=True).order_by("name")
    pets = (
        Pet.objects.filter(active=True, caretakers=caretaker, shelter__active=True)
        .select_related("shelter")
        .order_by("-created_at", "-id")
    )
    return render(
        request,
        "accounts/caretaker_detail.html",
        {"caretaker": caretaker, "shelters": shelters, "pets": pets},
    )


def caretaker_create(request):
    if request.method == "POST":
        form = CaretakerCreateForm(request.POST, request.FILES)
        if form.is_valid():
            caretaker = form.save()
            return redirect("caretaker-detail", pk=caretaker.pk)
    else:
        form = CaretakerCreateForm()

    return render(request, "accounts/create_caretaker.html", {"form": form})


def volunteer_create(request):
    if request.method == "POST":
        form = VolunteerCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("caretaker-list")
    else:
        form = VolunteerCreateForm()

    return render(request, "accounts/create_volunteer.html", {"form": form})


def caretaker_assign_pets(request, pk):
    caretaker = get_object_or_404(Caretaker.objects.filter(active=True), pk=pk)
    if request.method == "POST":
        form = PetAssignmentForm(request.POST, caretaker=caretaker)
        if form.is_valid():
            form.save()
            return redirect("caretaker-detail", pk=caretaker.pk)
    else:
        form = PetAssignmentForm(caretaker=caretaker)

    shelters = caretaker.shelters.filter(active=True).order_by("name")
    return render(
        request,
        "accounts/assign_pets.html",
        {"caretaker": caretaker, "form": form, "shelters": shelters},
    )


def caretaker_edit(request, pk):
    caretaker = get_object_or_404(Caretaker.objects.filter(active=True), pk=pk)
    if request.method == "POST":
        form = CaretakerEditForm(request.POST, request.FILES, instance=caretaker)
        if form.is_valid():
            caretaker = form.save()
            return redirect("caretaker-detail", pk=caretaker.pk)
    else:
        form = CaretakerEditForm(instance=caretaker)

    return render(
        request,
        "accounts/edit_caretaker.html",
        {"form": form, "caretaker": caretaker},
    )


def caretaker_delete(request, pk):
    caretaker = get_object_or_404(Caretaker, pk=pk)
    if request.method == "POST":
        caretaker.delete()
        return redirect("caretaker-list")
    return render(
        request,
        "accounts/confirm_delete.html",
        {"caretaker": caretaker},
    )
