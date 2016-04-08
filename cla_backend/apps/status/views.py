from django.db import connection, DatabaseError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer

from cla_common.smoketest import smoketest

import os


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def status(request):
    if request.method == 'GET':
        message = ''
        c = None
        try:
            c = connection.cursor()
            c.execute('SELECT 1')
            row = c.fetchone()
            db_ready = row[0] == 1
            return JSONResponse({
                'db': {
                    'ready': db_ready,
                    'message': message
                }
            })
        except DatabaseError as e:
            message = str(e)
        finally:
            if c:
                c.close()


@csrf_exempt
def ping(request):

    res = {
        'version_number': None,
        'build_date': None,
        'commit_id': None,
        'build_tag': None
    }

    try:
        res['version_number'] = os.environ['APPVERSION']
    except KeyError:
        pass

    try:
        res['build_date'] = os.environ['APP_BUILD_DATE']
    except KeyError:
        pass

    try:
        res['commit_id'] = os.environ['APP_GIT_COMMIT']
    except KeyError:
        pass

    try:
        res['build_tag'] = os.environ['APP_BUILD_TAG']
    except KeyError:
        pass

    return JSONResponse(res)



@csrf_exempt
def smoketests(request):
    """
    Run smoke tests and return results as JSON datastructure
    """
    from cla_backend.apps.status.tests.smoketests import SmokeTests

    return JSONResponse(smoketest(SmokeTests))
