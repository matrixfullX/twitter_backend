from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    template = 'home/home.html'
    cntx = {
        "activePage": "home",
        "frontend_url": settings.DOMAIN_FRONTEND,
    }
    return render(request, template, cntx)


def health(request):
    """Lightweight readiness endpoint for the cloud platform's health checks."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
