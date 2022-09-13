import datetime
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User

from ipware.ip import get_ip
from rest_framework.exceptions import Throttled

from oauth2_provider.views import TokenView as Oauth2AccessTokenView
from oauth2_provider.exceptions import OAuthToolkitError
from oauthlib.oauth2.rfc6749 import OAuth2Error

from .forms import ClientIdPasswordGrantForm
from .models import AccessAttempt
from .throttling import LoginRateThrottle

logger = logging.getLogger(__name__)


class AccessTokenView(Oauth2AccessTokenView):
    throttle_classes = [LoginRateThrottle]

    def __init__(self, *args, **kwargs):
        super(AccessTokenView, self).__init__(*args, **kwargs)
        self.account_lockedout = False

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
            self.check_login_attempts(request)
            self.check_user_is_active(request)
        except Throttled as exc:
            logger.info("login throttled: {}".format(self._get_request_log_extras(request)))
            response = self.error_response({"error": "throttled", "detail": exc.detail}, status=exc.status_code)

            if exc.wait:
                response["X-Throttle-Wait-Seconds"] = "%d" % exc.wait
            return response
        except OAuth2Error as exc:
            logger.info("User is inactive: {}".format(request.POST.get("username")))
            response = self.error_response({"error": exc.description}, status=401)
            return response

        response = super(AccessTokenView, self).dispatch(request, *args, **kwargs)
        if response.status_code > 399:
            self.on_invalid_attempt(request)
        else:
            self.on_valid_attempt(request)

        return response

    def on_invalid_attempt(self, request):
        if not self.account_lockedout:
            username = request.POST.get("username")
            if username:
                AccessAttempt.objects.create_for_username(username)

    def on_valid_attempt(self, request):
        username = request.POST.get("username")
        AccessAttempt.objects.delete_for_username(username)

    def check_user_is_active(self, request):
        user = None
        username = request.POST.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise OAuth2Error("invalid_client")

        if not user.is_active:
            raise OAuth2Error("account_disabled")

    def check_login_attempts(self, request):
        username = request.POST.get("username")

        cooloff_time = timezone.now() - datetime.timedelta(minutes=settings.LOGIN_FAILURE_COOLOFF_TIME)

        attempts = AccessAttempt.objects.filter(username=username, created__gt=cooloff_time).count()

        if attempts >= settings.LOGIN_FAILURE_LIMIT:
            self.account_lockedout = True

            logger.info("account locked out", extra={"username": username})

            raise OAuth2Error("locked_out")

    def get_password_grant(self, request, data, client):
        form = ClientIdPasswordGrantForm(data, client=client)
        if not form.is_valid():
            log_extras = self._get_request_log_extras(request)
            log_extras["FORM_ERRORS"] = form.errors
            logger.info("login failed: {}".format(json.dumps(log_extras)))

            form.on_form_invalid()

            raise OAuthToolkitError(form.errors)
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
        response = HttpResponse(json.dumps(error), content_type=content_type, status=status, **kwargs)
        message = "INVESTIGATE-LGA-1746: {} {}".format(response.status_code, response.content)
        logging.info(message)
        return response
