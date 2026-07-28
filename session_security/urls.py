from django.urls import path

from . import views


urlpatterns = [
    path("ping", views.ping, name="session_security_ping"),
    path("ping/", views.ping),
]
