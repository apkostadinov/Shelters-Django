from django.shortcuts import get_object_or_404, redirect, render

from pets.models import Pet

from .forms import (
    CaretakerCreateForm,
    CaretakerEditForm,
    PetAssignmentForm,
    VolunteerCreateForm,
    VolunteerEditForm,
)
from .models import Caretaker, Volunteer


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


def volunteer_list(request):
    volunteers = Volunteer.objects.filter(active=True).order_by("name")
    return render(request, "accounts/volunteer_list.html", {"volunteers": volunteers})


def volunteer_detail(request, pk):
    volunteer = get_object_or_404(Volunteer.objects.filter(active=True), pk=pk)
    return render(request, "accounts/volunteer_detail.html", {"volunteer": volunteer})


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


def volunteer_edit(request, pk):
    volunteer = get_object_or_404(Volunteer.objects.filter(active=True), pk=pk)
    if request.method == "POST":
        form = VolunteerEditForm(request.POST, request.FILES, instance=volunteer)
        if form.is_valid():
            volunteer = form.save()
            return redirect("volunteer-detail", pk=volunteer.pk)
    else:
        form = VolunteerEditForm(instance=volunteer)

    return render(
        request,
        "accounts/edit_volunteer.html",
        {"form": form, "volunteer": volunteer},
    )


def volunteer_delete(request, pk):
    volunteer = get_object_or_404(Volunteer, pk=pk)
    if request.method == "POST":
        volunteer.delete()
        return redirect("volunteer-list")
    return render(
        request,
        "accounts/confirm_delete.html",
        {"volunteer": volunteer},
    )
