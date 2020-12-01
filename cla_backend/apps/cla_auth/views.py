import logging

from ipware.ip import get_ip
from rest_framework.exceptions import Throttled

from provider.oauth2.views import AccessTokenView as Oauth2AccessTokenView
from provider.views import OAuthError

from .forms import ClientIdPasswordGrantForm
from .throttling import LoginRateThrottle

logger = logging.getLogger(__name__)


class AccessTokenView(Oauth2AccessTokenView):
    throttle_classes = [LoginRateThrottle]

    def get_throttles(self):
        """
        Instantiates and returns the list of throttles that this view uses.
        """
        return [throttle() for throttle in self.throttle_classes]

    def check_throttles(self, request):
        """
        Check if request should be throttled.
        Raises an appropriate exception if the request is throttled.
        """
        for throttle in self.get_throttles():
            if not throttle.allow_request(request, self):
                self.throttled(request, throttle.wait())

    def throttled(self, request, wait):
        """
        If request is throttled, determine what kind of exception to raise.
        """
        raise Throttled(wait)

    def dispatch(self, request, *args, **kwargs):
        try:
            self.check_throttles(request)
        except Throttled as exc:
            logger.info(
                "login throttled",
                extra={
                    "IP": get_ip(request),
                    "HTTP_REFERER": request.META.get("HTTP_REFERER"),
                    "HTTP_USER_AGENT": request.META.get("HTTP_USER_AGENT"),
                },
            )
            response = self.error_response({"error": "throttled", "detail": exc.detail}, status=exc.status_code)

            if exc.wait:
                response["X-Throttle-Wait-Seconds"] = "%d" % exc.wait
            return response

        return super(AccessTokenView, self).dispatch(request, *args, **kwargs)

    def get_password_grant(self, request, data, client):
        form = ClientIdPasswordGrantForm(data, client=client)
        if not form.is_valid():
            logger.info(
                "login failed",
                extra={
                    "IP": get_ip(request),
                    "USERNAME": request.POST.get("username"),
                    "CLIENT_SECRET": request.POST.get("client_secret"),
                    "HTTP_REFERER": request.META.get("HTTP_REFERER"),
                    "HTTP_USER_AGENT": request.META.get("HTTP_USER_AGENT"),
                },
            )

            form.on_form_invalid()

            raise OAuthError(form.errors)
        else:
            form.on_form_valid()

        logger.info(
            "login succeeded",
            extra={
                "IP": get_ip(request),
                "USERNAME": request.POST.get("username"),
                "CLIENT_SECRET": request.POST.get("client_secret"),
                "HTTP_REFERER": request.META.get("HTTP_REFERER"),
                "HTTP_USER_AGENT": request.META.get("HTTP_USER_AGENT"),
            },
        )
        return form.cleaned_data
