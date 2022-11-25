import re

from django.conf import settings
from django.core.urlresolvers import reverse
from session_security.middleware import SessionSecurityMiddleware


class ClaSessionSecurityMiddleware(SessionSecurityMiddleware):
    """
    Extends session_security and adds the ability to specify passive urls via regular expression.
    """

    def __init__(self):
        self.PASSIVE_URL_REGEX_LIST = getattr(settings, "PASSIVE_URL_REGEX_LIST", [])
        super(ClaSessionSecurityMiddleware, self).__init__()

    def _is_passive_request(self, request):

        url_match_found = any(re.search(url_check, request.path) for url_check in self.PASSIVE_URL_REGEX_LIST)

        if url_match_found and not request.path == reverse('session_security_ping'):
            return True

        return False

    def process_request(self, request):

        if self._is_passive_request(request):
            return

        super(ClaSessionSecurityMiddleware, self).process_request(request)
