import logging
from django.db import connection, DatabaseError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from django.views.generic import TemplateView

from cla_common.smoketest import smoketest
from moj_irat.views import PingJsonView as BasePingJsonView


logger = logging.getLogger(__name__)


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs["content_type"] = "application/json"
        super(JSONResponse, self).__init__(content, **kwargs)


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


class PingJsonView(BasePingJsonView):
    CONTRACT_2018_ENABLED_key = None


class MaintenanceModeView(TemplateView):
    template_name = "maintenance.html"

    def dispatch(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=503)
