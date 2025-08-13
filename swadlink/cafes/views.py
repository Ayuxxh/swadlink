
from django.shortcuts import render, get_object_or_404

from django.http import JsonResponse
from django.views import View
from .models import Cafe 
from utils.decorators import owner_employee_or_admin_required

def landing(request):
    return render(request, 'cafes/landing.html')




from django.conf import settings



def generate_manifest( request, slug ):
    cafe = get_object_or_404(Cafe,slug=slug)
    manifest = {
        "name": f"{cafe.name} POS",  # e.g., "paris-louvre" → "Paris Louvre PWA"
        "short_name": cafe.name[:12],  # Truncated slug
        "start_url": f"/{slug}/login",  # Deep link to this café
        "theme_color": settings.PWA_APP_THEME_COLOR,  # Reuse global settings
        "background_color": settings.PWA_APP_BACKGROUND_COLOR,
        "display": settings.PWA_APP_DISPLAY,
        "icons": settings.PWA_APP_ICONS,  # <-- Reuse global icons
    }
    return JsonResponse(manifest, content_type='application/manifest+json')