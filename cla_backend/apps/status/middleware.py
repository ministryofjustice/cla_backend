from django.conf import settings
from django.shortcuts import redirect


class MaintenanceModeMiddleware(object):
    MAINTENANCE_PATH = "/maintenance"
    EXEMPT_PATHS = [
        "/status",
        "/status/ping.json",
        "/status/status.json",
        "/status/healthcheck.json",
        MAINTENANCE_PATH,
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response is not None:
            return response
        return self.get_response(request)

    def process_request(self, request):
        maintenance_mode = getattr(settings, "MAINTENANCE_MODE", False)
        if maintenance_mode and request.path not in self.EXEMPT_PATHS:
            return redirect(self.MAINTENANCE_PATH)
        if not maintenance_mode and request.path == self.MAINTENANCE_PATH:
            return redirect("/admin")
