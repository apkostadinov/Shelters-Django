from django.shortcuts import get_object_or_404, render

from .models import Pet


def pet_list(request):
    pets = Pet.objects.select_related("shelter").prefetch_related("caretakers")
    return render(request, "pets/list.html", {"pets": pets})


def pet_detail(request, pk):
    pet = get_object_or_404(
        Pet.objects.select_related("shelter").prefetch_related("caretakers"),
        pk=pk,
    )
    return render(request, "pets/detail.html", {"pet": pet})
