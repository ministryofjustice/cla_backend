import datetime
import json
import logging

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User

from ipware.ip import get_ip
from rest_framework.exceptions import Throttled

from call_centre.models import Operator
from cla_provider.models import Staff

from oauth2_provider.models import Application
from oauth2_provider.views import TokenView as Oauth2AccessTokenView
from oauthlib.oauth2.rfc6749 import OAuth2Error

from .models import AccessAttempt
from .throttling import LoginRateThrottle

logger = logging.getLogger(__name__)


class AccessTokenView(Oauth2AccessTokenView):
    throttle_classes = [LoginRateThrottle]

    def __init__(self, *args, **kwargs):
        super(AccessTokenView, self).__init__(*args, **kwargs)

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
            self.check_user_against_model(request)
        except Throttled as exc:
            logger.info("login throttled: {}".format(self._get_request_log_extras(request)))
            response = self.error_response({"error": "throttled", "detail": exc.detail}, status=exc.status_code)

            if exc.wait:
                response["X-Throttle-Wait-Seconds"] = "%d" % exc.wait
            return response
        except OAuth2Error as exc:
            logger.info("User: {}; Error: {}".format(request.POST.get("username"), exc.description))
            response = self.error_response({"error": exc.description}, status=401)
            return response

        response = super(AccessTokenView, self).dispatch(request, *args, **kwargs)
        if response.status_code > 399:
            self.on_invalid_attempt(request)
        else:
            self.on_valid_attempt(request)
            # Add user details to successful response
            response = self.add_user_details_to_response(request, response)

        return response

    def on_invalid_attempt(self, request):
        """
        This creates an invalid access attempt, these get checked and counted
        each time a user attempts to login.
        """

        username = request.POST.get("username")
        if username:
            AccessAttempt.objects.create_for_username(username)

    def on_valid_attempt(self, request):
        """
        When a user has successfully logged in deletes the login attempts made
        to keep the table clear.
        """
        username = request.POST.get("username")
        AccessAttempt.objects.delete_for_username(username)

    def check_user_is_active(self, request):
        """
        This checks that the user is set to active
        """
        username = request.POST.get("username")
        try:
            user = User.objects.filter(Q(username=username)).first()
            if not user:
                raise User.DoesNotExist
        except User.DoesNotExist:
            raise OAuth2Error("invalid_client")

        if not user.is_active:
            raise OAuth2Error("account_disabled")

    def check_user_against_model(self, request):
        """
        This is more for the frontend, it tries to log the user in as an operator first
        if that fails, it tries to log in the user as a provider.  It uses this to find
        where to send the user.
        """
        # Initial getting the client, if client doesnt exist we catch the error
        client_id = request.POST.get("client_id")
        try:
            client = Application.objects.filter(Q(client_id=client_id)).first()
            if not client:
                raise Application.DoesNotExist
        except Application.DoesNotExist:
            raise OAuth2Error("invalid_client")

        class_name = self.get_user_model(client.name)
        username = request.POST.get("username")

        try:
            user_instance = class_name.objects.filter(Q(user__username=username)).first()
            if not user_instance:
                raise class_name.DoesNotExist
        except class_name.DoesNotExist:
            raise OAuth2Error("invalid_grant")

    def get_user_model(self, client_name):
        """
        This gets the appropriate model for the client/application name.
        """
        class_name = None
        if client_name == "operator":
            class_name = Operator
        elif client_name == "staff":
            class_name = Staff
        else:
            raise OAuth2Error("invalid_grant")

        return class_name

    def check_login_attempts(self, request):
        """
        This checks how many login attempts there have been, it locks the user out when the
        LOGIN_FAILURE_LIMIT has been hit.
        """
        username = request.POST.get("username")

        cool_off_time = timezone.now() - datetime.timedelta(minutes=settings.LOGIN_FAILURE_COOLOFF_TIME)

        attempts = AccessAttempt.objects.filter(Q(username=username) & Q(created__gt=cool_off_time)).count()

        if attempts >= settings.LOGIN_FAILURE_LIMIT:

            logger.info("account locked out", extra={"username": username})

            raise OAuth2Error("locked_out")

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
        """
        This constructs an error response into a http response.
        """
        response = HttpResponse(json.dumps(error), content_type=content_type, status=status, **kwargs)

        return response

    def _get_operator_data(self, user):
        """
        Get serialized operator data.
        """
        try:
            from call_centre.serializers import OperatorSerializer

            operator = Operator.objects.filter(Q(user=user)).first()
            if not operator:
                raise Operator.DoesNotExist
            serializer = OperatorSerializer(operator)
            user_data = serializer.data
            user_data["user_type"] = "operator"
            return user_data
        except Operator.DoesNotExist:
            logger.warning("Operator not found for user", extra={"username": user.username})
            return None

    def _get_staff_data(self, user):
        """
        Get serialized staff data.
        """
        try:
            from cla_provider.serializers import StaffSerializer

            staff = Staff.objects.filter(Q(user=user)).first()
            if not staff:
                raise Staff.DoesNotExist
            serializer = StaffSerializer(staff)
            user_data = serializer.data
            user_data["user_type"] = "staff"
            return user_data
        except Staff.DoesNotExist:
            logger.warning("Staff not found for user", extra={"username": user.username})
            return None

    def _get_user_data_by_client_type(self, user, client_name):
        """
        Get user data based on client type.
        """
        if client_name == "operator":
            return self._get_operator_data(user)
        elif client_name == "staff":
            return self._get_staff_data(user)
        return None

    def add_user_details_to_response(self, request, response):
        """
        Add logged-in user details to the access token response.
        """
        username = request.POST.get("username")
        client_id = request.POST.get("client_id")

        if not username:
            logger.warning("No username found in request")
            return response

        try:
            user = User.objects.filter(Q(username=username)).first()
            if not user:
                logger.warning("User not found", extra={"username": username})
                return response

            client = Application.objects.filter(Q(client_id=client_id)).first()
            if not client:
                logger.warning("Client not found", extra={"client_id": client_id})
                return response

            logger.info("Getting user data for authentication", extra={"client_name": client.name, "username": username})

            user_data = self._get_user_data_by_client_type(user, client.name)

            if not user_data:
                logger.warning("No user data returned", extra={"username": username, "client_name": client.name})
                return response

            # Decode response content if it's bytes
            content = response.content
            if isinstance(content, bytes):
                content = content.decode("utf-8")

            response_data = json.loads(content)
            response_data["user"] = user_data
            response.content = json.dumps(response_data, cls=DjangoJSONEncoder)

            logger.info("Successfully added user details to response")

        except Exception as e:
            # Log error but don't fail the authentication
            logger.error("Error adding user details to response", exc_info=True, extra={"error": str(e)})

        return response
