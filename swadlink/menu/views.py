from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, render
from cafes.models import Cafe
from .models import Menu

def menu(request, slug):
    cafe = get_object_or_404(Cafe, slug=slug)
    menu_items = Menu.objects.filter(cafe=cafe)

    context = {
                'menu_items': menu_items,
        'cafe': cafe,
    }
    return render(request, 'menu/menu.html', context)