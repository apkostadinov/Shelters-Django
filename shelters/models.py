from django.db import models


class Shelter(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.TextField()
    capacity = models.PositiveIntegerField()
