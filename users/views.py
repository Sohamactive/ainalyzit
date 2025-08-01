# users/views.py

from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode
from ainalyzit.settings import oauth # Import the oauth instance

import os

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("users:callback"))
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(reverse("dashboard:dashboard")) # Redirect to dashboard after login

def logout(request):
    request.session.clear()
    domain = os.getenv("AUTH0_DOMAIN")
    client_id = os.getenv("AUTH0_CLIENT_ID")
    return_to = request.build_absolute_uri(reverse("analysis:index"))
    logout_url = f"https://{domain}/v2/logout?" + urlencode(
        {"returnTo": return_to, "client_id": client_id},
    )
    return redirect(logout_url)
