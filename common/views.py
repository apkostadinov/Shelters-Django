from django.db.models import Prefetch
from django.views.generic import TemplateView

from accounts.models import Caretaker
from pets.models import Pet
from shelters.models import Shelter


class HomePageView(TemplateView):
    template_name = "common/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        context["shelter"] = shelter
        context["pets"] = pets
        return context
