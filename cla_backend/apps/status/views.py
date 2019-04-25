from django.db import connection, DatabaseError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer

from cla_common.smoketest import smoketest
from moj_irat.views import JsonResponse, PingJsonView as BasePingJsonView
from django.conf import settings
import os


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
    def get(self, request):
        response_data = {
            attr[:-4]: os.environ.get(getattr(self, attr))
            for attr in dir(self)
            if attr.endswith("_key") and getattr(self, attr)
        }
        response_data["2018_contracts_enabled"] = settings.CONTRACT_2018_ENABLED
        response = JsonResponse(response_data)
        if not response_data["build_date"] or not response_data["commit_id"]:
            response.status_code = 501
        return response
