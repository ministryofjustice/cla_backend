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

    def process_request(self, request):
        maintenance_mode = getattr(settings, "MAINTENANCE_MODE", False)
        if maintenance_mode and request.path not in self.EXEMPT_PATHS:
            return redirect(self.MAINTENANCE_PATH)
        if not maintenance_mode and request.path == self.MAINTENANCE_PATH:
            return redirect("/admin")
