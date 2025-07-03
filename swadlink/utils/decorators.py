from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth import REDIRECT_FIELD_NAME

def login_required_with_slug(view_func):
    @wraps(view_func)
    def _wrapped_view(request, slug, *args, **kwargs):
        if not request.user.is_authenticated:
            # Redirect to /<slug>/login/?next=current_path
            return redirect(f'/{slug}/login/?{REDIRECT_FIELD_NAME}={request.path}')
        return view_func(request, slug, *args, **kwargs)
    return _wrapped_view


from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import REDIRECT_FIELD_NAME
from cafes.models import Cafe

def owner_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, slug, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/{slug}/login/?{REDIRECT_FIELD_NAME}={request.path}')
        
        cafe = get_object_or_404(Cafe, slug=slug)

        # ❗ Check if the logged-in user is an owner of this cafe
        if request.user not in cafe.owners.all():
            return HttpResponseForbidden("You do not have permission to access this dashboard.")

        # ✅ Pass cafe and slug and owner into the view
        return view_func(request, cafe=cafe, owner=request.user, slug=slug, *args, **kwargs)

    return _wrapped_view


from urllib.parse import quote


def owner_or_superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, slug, *args, **kwargs):
        print("User:", request.user)
        print("Authenticated:", request.user.is_authenticated)
        print("Superuser:", request.user.is_superuser)
        print("Slug:", slug)
        if not request.user.is_authenticated:
            # preserve ?next= on redirect
            path = quote(request.get_full_path())

            return redirect(f'/{slug}/login/?next={path}')
        
        cafe = get_object_or_404(Cafe, slug=slug)
        print("Cafe found:", cafe)

        # ✅ Allow if user is an owner of the cafe
        if request.user in cafe.owners.all():
            return view_func(request, cafe=cafe, owner=request.user, slug=slug, *args, **kwargs)

        # ✅ Also allow if user is a superuser
        if request.user.is_superuser:
            return view_func(request, cafe=cafe, owner=request.user, slug=slug, *args, **kwargs)

        # ❌ Otherwise forbid access
        return HttpResponseForbidden("You do not have permission to access this dashboard.")

    return _wrapped_view
