import logging
from json import dumps

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler
from django.http import HttpResponse

from mohawk.exc import TokenExpired

log = logging.getLogger(__name__)


class OBIEEHawkResponseMiddleware:

    def process_exception(self, request, exception):
        if isinstance(exception, TokenExpired):
            resp = HttpResponse(dumps({'detail': 'invalid timestamp'}),
                                status=401,
                                content_type='application/json')
            resp['WWW-Authenticate'] = exception.www_authenticate
            return resp
        return None

    def process_response(self, request, response):
        is_hawk_request = request.META.get(
            'HTTP_AUTHORIZATION', '').startswith('Hawk')
        receiver = request.META.get('hawk.receiver', None)

        if is_hawk_request:
            if receiver:
                # Sign our response, so clients can trust us.
                log.debug('Hawk signing the response')
                receiver.respond(content=response.content,
                                 content_type=response['Content-Type'])
                response['Server-Authorization'] = receiver.response_header
            else:
                log.debug('Hawk auth present in header but receiver missing, '
                          'not signing')
        else:
            log.debug('NOT Hawk signing the response, not a Hawk request')

        return response
