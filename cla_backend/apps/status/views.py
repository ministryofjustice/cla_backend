import logging
import os
from django.db import connection, DatabaseError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from django.views import View
from django.views.generic import TemplateView

from cla_common.smoketest import smoketest
from .healthcheck_registry import registry

logger = logging.getLogger(__name__)


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs["content_type"] = "application/json"
        super(JSONResponse, self).__init__(content, **kwargs)


class PingJsonView(View):
    build_date_key = None
    commit_id_key = None
    version_number_key = None
    build_tag_key = None
    CONTRACT_2018_ENABLED_key = None

    def get(self, request, *args, **kwargs):
        payload = {}
        for field_name in (
            "build_date_key",
            "commit_id_key",
            "version_number_key",
            "build_tag_key",
            "CONTRACT_2018_ENABLED_key",
        ):
            env_key = getattr(self, field_name, None)
            if env_key:
                payload[field_name.replace("_key", "")] = os.environ.get(env_key, "")
        return JSONResponse(payload)


class HealthcheckView(View):
    def get(self, request, *args, **kwargs):
        registry.load_healthchecks()
        results = {}
        overall_status = True

        for healthcheck in registry._registry:
            try:
                is_healthy = bool(healthcheck())
            except Exception as exc:  # pragma: no cover - defensive path for runtime probes
                logger.exception("Healthcheck %s failed", healthcheck.__name__)
                is_healthy = False
                results[healthcheck.__name__] = {"ok": is_healthy, "message": str(exc)}
            else:
                results[healthcheck.__name__] = {"ok": is_healthy}

            overall_status = overall_status and is_healthy

        status_code = 200 if overall_status else 500
        return JSONResponse({"ok": overall_status, "checks": results}, status=status_code)


@csrf_exempt
def status(request):
    if request.method == "GET":
        message = ""
        c = None
        try:
            c = connection.cursor()
            c.execute("SELECT 1")
            row = c.fetchone()
            db_ready = row[0] == 1
            return JSONResponse({"db": {"ready": db_ready, "message": message}})
        except DatabaseError as e:
            message = str(e)
            logger.error(message)
        finally:
            if c:
                c.close()


@csrf_exempt
def smoketests(request):
    """
    Run smoke tests and return results as JSON datastructure
    """
    from cla_backend.apps.status.tests.smoketests import SmokeTests

    return JSONResponse(smoketest(SmokeTests))


class MaintenanceModeView(TemplateView):
    template_name = "maintenance.html"

    def dispatch(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=503)
