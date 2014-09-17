import logging

from django_statsd.clients import statsd
from ipware.ip import get_ip

from provider.oauth2.views import AccessTokenView as Oauth2AccessTokenView
from provider.views import OAuthError

from .forms import ClientIdPasswordGrantForm

logger = logging.getLogger(__name__)


class AccessTokenView(Oauth2AccessTokenView):
    def get_password_grant(self, request, data, client):
        form = ClientIdPasswordGrantForm(data, client=client)
        if not form.is_valid():
            statsd.incr('login.failed')
            logger.info('login failed', extra={
                'IP': get_ip(request),
                'USERNAME': request.POST.get('username'),
                'CLIENT_SECRET': request.POST.get('client_secret'),
                'HTTP_REFERER': request.META.get('HTTP_REFERER'),
                'HTTP_USER_AGENT': request.META.get('HTTP_USER_AGENT')
            })
            raise OAuthError(form.errors)

        statsd.incr('login.success')
        logger.info('login succeeded', extra={
            'IP': get_ip(request),
            'USERNAME': request.POST.get('username'),
            'CLIENT_SECRET': request.POST.get('client_secret'),
            'HTTP_REFERER': request.META.get('HTTP_REFERER'),
            'HTTP_USER_AGENT': request.META.get('HTTP_USER_AGENT')
        })
        return form.cleaned_data
