import re

from django.conf import settings

from session_security.middleware import SessionSecurityMiddleware

PASSIVE_URL_REGEX_LIST = getattr(settings, "PASSIVE_URL_REGEX_LIST", None)


class ClaSessionSecurityMiddleware(SessionSecurityMiddleware):
    """
    Extends session_security and adds the ability to specify passive urls via regular expression.
    """

    def __init__(self):
        super(ClaSessionSecurityMiddleware, self).__init__()

    def is_passive_request(self, request):

        if any(re.search(url_check, request.path) for url_check in PASSIVE_URL_REGEX_LIST):
            return True

        return False

    def process_request(self, request):

        if self.is_passive_request(request):
            return

        super(ClaSessionSecurityMiddleware, self).process_request(request)
