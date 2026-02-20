from django.conf import settings
from django.db import models


def shelter_image_upload_to(instance, filename):
    return f"shelters/{instance.pk}/{filename}"


class Shelter(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.TextField()
    image = models.ImageField(upload_to=shelter_image_upload_to, blank=True)
    capacity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if self.image and self.pk is None:
            image = self.image
            self.image = None
            super().save(*args, **kwargs)
            self.image = image
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return f"{settings.MEDIA_URL}defaults/shelters.png"
