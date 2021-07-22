import logging
import json

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
            logger.info("login throttled: {}".format(self._get_request_log_extras(request)))
            response = self.error_response({"error": "throttled", "detail": exc.detail}, status=exc.status_code)

            if exc.wait:
                response["X-Throttle-Wait-Seconds"] = "%d" % exc.wait
            return response

        return super(AccessTokenView, self).dispatch(request, *args, **kwargs)

    def get_password_grant(self, request, data, client):
        form = ClientIdPasswordGrantForm(data, client=client)
        if not form.is_valid():
            log_extras = self._get_request_log_extras(request)
            log_extras["FORM_ERRORS"] = form.errors
            logger.info("login failed: {}".format(json.dumps(log_extras)))

            form.on_form_invalid()

            raise OAuthError(form.errors)
        else:
            form.on_form_valid()

        logger.info("login succeeded: {}".format(json.dumps(self._get_request_log_extras(request))))
        return form.cleaned_data

    def _get_request_log_extras(self, request):
        return {
            "IP": get_ip(request),
            "USERNAME": request.POST.get("username"),
            "CLIENT_ID": request.POST.get("client_id"),
            "GRANT_TYPE": request.POST.get("grant_type"),
            "HTTP_REFERER": request.META.get("HTTP_REFERER"),
            "HTTP_USER_AGENT": request.META.get("HTTP_USER_AGENT"),
        }

    def error_response(self, error, content_type="application/json", status=400, **kwargs):
        response = super(AccessTokenView, self).error_response(error, content_type, status, **kwargs)
        message = "INVESTIGATE-LGA-1746: {} {}".format(response.status_code, response.content)
        logging.info(message)
        return response
