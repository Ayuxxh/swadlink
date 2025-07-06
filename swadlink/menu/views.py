from django.shortcuts import render

def menu(request, slug):
    return render(request, 'menu/menu.html')