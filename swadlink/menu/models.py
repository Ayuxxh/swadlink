from django.db import models
from cafes.models import Cafe


class Menu(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='menu')

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_veg = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.cafe.name}"


