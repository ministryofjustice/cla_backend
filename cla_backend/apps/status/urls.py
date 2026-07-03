from cla_backend.libs.django_compat import patterns, url
from django.conf import settings
from . import views

app_name = "status"

urlpatterns = patterns(
    "",
    url(r"^$", views.status),
    url(r"^status.json$", views.smoketests),
    url(r"^ping.json$", views.PingJsonView.as_view(**settings.PING_JSON_KEYS), name="ping_json"),
    url(r"^healthcheck.json$", views.HealthcheckView.as_view(), name="healthcheck_json"),
)
