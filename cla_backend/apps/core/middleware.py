from django.http import Http404
from django_statsd.clients import statsd


class GraphiteMiddleware(object):
    def process_response(self, request, response):
        statsd.incr('response.%s' % response.status_code)
        return response

    def process_exception(self, request, exception):
        if not isinstance(exception, Http404):
            statsd.incr('response.500')
