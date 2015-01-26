import logging
import sys
import traceback

from django.conf import settings

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from provider.oauth2.models import Client

from mohawk import Receiver
from mohawk.exc import HawkFail, TokenExpired
from mohawk.util import parse_authorization_header

from hawkrest import seen_nonce

log = logging.getLogger(__name__)
# Number of seconds until a Hawkmessage expires.
default_message_expiration = 60


class OBIEEHawkAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if not request.META.get('HTTP_AUTHORIZATION'):
            log.debug('request did not send an Authorization header')
            raise AuthenticationFailed('missing authorization header')

        try:
            receiver = Receiver(
                lookup_credentials,
                request.META['HTTP_AUTHORIZATION'],
                request.build_absolute_uri(),
                request.method,
                content=request.body,
                seen_nonce=(seen_nonce
                            if getattr(settings, 'USE_CACHE_FOR_HAWK_NONCE',
                                       True)
                            else None),
                content_type=request.META.get('CONTENT_TYPE', ''),
                timestamp_skew_in_seconds=getattr(settings,
                                                  'HAWK_MESSAGE_EXPIRATION',
                                                  default_message_expiration))
        except TokenExpired as expiry:
            raise
        except HawkFail:
            etype, val, tb = sys.exc_info()
            log.debug(traceback.format_exc())
            log.info('Hawk: denying access because of '
                     '{etype}: {val}'.format(etype=etype, val=val))
            raise AuthenticationFailed('authentication failed')

        # Pass our receiver object to the middleware so the request header
        # doesn't need to be parsed again.
        request.META['hawk.receiver'] = receiver

        # get User from Hawk id in HTTP Authorization header
        try:
            client_id = parse_authorization_header(
                request.META['HTTP_AUTHORIZATION'])['id']
            client = Client.objects.get(client_id=client_id)
            return (client.user, None)
        except (KeyError, Client.DoesNotExist):
            return None


def lookup_credentials(cr_id):
    try:
        client = Client.objects.get(client_id=cr_id)
        return {
            'id': cr_id,
            'key': client.client_secret,
            'algorithm': 'sha256'
        }
    except Client.DoesNotExist:
        raise LookupError('No Hawk ID of {id}'.format(id=cr_id))
