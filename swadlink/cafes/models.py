from django.db import models
from django.utils.text import slugify
from accounts.models import CustomUser



    
class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        
        return f"{self.name}, {self.state.name}"
    
class Cafe(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    secondary_phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField()
    date_joined = models.DateTimeField(auto_now_add=True)

    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=False, related_name='cafes')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=False, related_name='cafes')


    owners = models.ManyToManyField(
        CustomUser,
        related_name='cafes_owned',
        limit_choices_to={'role': 'owner'}
    )
    employees = models.ManyToManyField(
        CustomUser,
        related_name='cafes_employed',
        limit_choices_to={'role': 'employee'},
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name