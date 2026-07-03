from django.utils import timezone


SESSION_KEY = "_session_security_last_activity"


class SessionSecurityMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = None
        if hasattr(self, "process_request"):
            response = self.process_request(request)
        if response is not None:
            return response
        if self.get_response is None:
            return None
        return self.get_response(request)

    def process_request(self, request):
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return None

        request.session[SESSION_KEY] = int(timezone.now().timestamp())
        return None
