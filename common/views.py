from django.db.models import Prefetch
from django.shortcuts import render

from accounts.models import Caretaker
from pets.models import Pet
from shelters.models import Shelter

def homepage(request):
    shelter = (
        Shelter.objects.filter(active=True)
        .prefetch_related(Prefetch("caretakers", queryset=Caretaker.objects.filter(active=True)))
        .order_by("?")
        .first()
    )
    pets = []
    if shelter:
        pets = (
            Pet.objects.filter(active=True, shelter=shelter)
            .select_related("shelter")
            .order_by("-created_at", "-id")[:3]
        )
    return render(request, "common/home.html", {"shelter": shelter, "pets": pets})
