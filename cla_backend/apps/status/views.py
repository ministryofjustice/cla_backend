from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer


class JSONResponse(HttpResponse):

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def status(request):
    if request.method == 'GET':
        message = ''
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
            c.close()
