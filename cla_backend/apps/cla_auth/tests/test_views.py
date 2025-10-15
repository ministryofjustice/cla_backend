import datetime
import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.test import TestCase
from django.conf import settings
from django.utils import timezone
import mock

from oauth2_provider.models import Application
from core.tests.mommy_utils import make_recipe
from cla_provider.models import Staff
from call_centre.models import Operator
from cla_auth.models import AccessAttempt


class LoginTestCase(TestCase):
    INVALID_GRANT_ERROR = '{"error": "invalid_grant"}'
    INVALID_CLIENT_ERROR = '{"error": "invalid_client"}'
    INVALID_CREDENTIALS_ERROR = '{"error_description": "Invalid credentials given.", "error": "invalid_grant"}'

    def setUp(self):
        super(LoginTestCase, self).setUp()

        self.url = reverse("oauth2:access_token")

        # setting up 2 clients

        self.op_username = "operator"
        self.op_email = "lennon@thebeatles.com"
        self.op_password = "operator"
        self.op_user = User.objects.create_user(self.op_username, self.op_email, self.op_password)
        self.op = Operator.objects.create(user=self.op_user)

        self.staff_username = "provider"
        self.staff_email = "lennon@thebeatles.com"
        self.staff_password = "provider"
        self.staff_user = User.objects.create_user(self.staff_username, self.staff_email, self.staff_password)

        self.prov = make_recipe("cla_provider.provider")
        self.staff = Staff.objects.create(user=self.staff_user, provider=self.prov)
        self.prov.save()

        # create an operator API client
        self.op_client = Application.objects.create(
            user=self.op_user,
            name="operator",
            client_type=0,
            client_id="call_centre",
            client_secret="secret",
            redirect_uris="http://localhost/redirect",
            authorization_grant_type="password",
        )

        # create an staff API client
        self.staff_api_client = Application.objects.create(
            user=self.staff_user,
            name="staff",
            client_type=0,
            client_id="cla_provider",
            client_secret="secret",
            redirect_uris="http://provider.localhost/redirect",
            authorization_grant_type="password",
        )

    def get_data(self, **kwargs):
        defaults = {"client_secret": "secret", "grant_type": "password"}
        defaults.update(kwargs)
        return defaults

    def get_operator_data(self, **kwargs):
        data = {"client_id": "call_centre", "username": "operator", "password": "operator"}
        data.update(kwargs)
        return self.get_data(**data)

    def get_provider_data(self, **kwargs):
        data = {"client_id": "cla_provider", "username": "provider", "password": "provider"}
        data.update(kwargs)
        return self.get_data(**data)

    def test_invalid_client_id(self):
        # invalid client_id
        self.assert_unauthorised_response(self.get_operator_data(client_id="invalid"), self.INVALID_CLIENT_ERROR)

    def test_invalid_client_secret(self):
        self.assert_unauthorised_response(self.get_operator_data(client_secret="invalid"), self.INVALID_CLIENT_ERROR)

    def test_client_name_doesnt_match_any_user_model(self):
        # Create api client with name that doesnt match a user model
        self.test_api_client = Application.objects.create(
            user=self.op_user,
            name="test",
            client_type=0,
            client_id="test",
            client_secret="secret",
            redirect_uris="http://provider.localhost/redirect",
            authorization_grant_type="password",
        )

        data = {"client_id": "test", "username": "operator", "password": "operator"}
        self.assert_unauthorised_response(data, self.INVALID_GRANT_ERROR)

    def test_operator_success(self):
        response = self.client.post(self.url, data=self.get_operator_data())
        self.assertEqual(response.status_code, 200)

        # Check that user details are included in response
        response_data = json.loads(response.content)
        self.assertIn("user", response_data)
        self.assertEqual(response_data["user"]["user_type"], "operator")
        self.assertEqual(response_data["user"]["username"], self.op_username)
        self.assertEqual(response_data["user"]["email"], self.op_email)

    def test_operator_invalid_password(self):
        response = self.client.post(self.url, data=self.get_operator_data(password="invalid"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, self.INVALID_CREDENTIALS_ERROR)

    def test_staff_success(self):
        response = self.client.post(self.url, data=self.get_provider_data())

        self.assertEqual(response.status_code, 200)

        # Check that user details are included in response
        response_data = json.loads(response.content)
        self.assertIn("user", response_data)
        self.assertEqual(response_data["user"]["user_type"], "staff")
        self.assertEqual(response_data["user"]["username"], self.staff_username)
        self.assertEqual(response_data["user"]["email"], self.staff_email)

    def test_staff_invalid_password(self):
        response = self.client.post(self.url, data=self.get_provider_data(password="invalid"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, self.INVALID_CREDENTIALS_ERROR)

    def test_locks_user_out_after_n_attempts(self):
        self.assertEqual(AccessAttempt.objects.count(), 0)

        for index in range(settings.LOGIN_FAILURE_LIMIT):
            response = self.client.post(self.url, data=self.get_operator_data(password="invalid"))
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.content, self.INVALID_CREDENTIALS_ERROR)
        self.assertEqual(AccessAttempt.objects.count(), settings.LOGIN_FAILURE_LIMIT)

        # the n-th time, the user's account will be locked out
        response = self.client.post(self.url, data=self.get_operator_data(password="invalid"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, '{"error": "locked_out"}')

        # from now on, even if the password is corrent, the account is locked
        response = self.client.post(self.url, data=self.get_operator_data())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, '{"error": "locked_out"}')

        with mock.patch("cla_auth.views.timezone") as mocked_timezone:
            mocked_timezone.now.return_value = timezone.now() + datetime.timedelta(
                minutes=settings.LOGIN_FAILURE_COOLOFF_TIME
            )
            response = self.client.post(self.url, data=self.get_operator_data())
            self.assertEqual(response.status_code, 200)

            self.assertEqual(AccessAttempt.objects.count(), 0)

    def test_throttling(self):
        # clearing cache
        cache.clear()

        # mocking throttle value
        from cla_auth.views import LoginRateThrottle

        with mock.patch.dict(LoginRateThrottle.THROTTLE_RATES, {"login": "1/sec"}):

            # 1st time => 200
            response = self.client.post(self.url, data=self.get_operator_data())
            self.assertEqual(response.status_code, 200)

            # 2nd time => 429
            response = self.client.post(self.url, data=self.get_operator_data())
            self.assertEqual(response.status_code, 429)

    def test_inactive_operator_failure(self):
        # active operator => success
        data = self.get_operator_data()
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

        # inactive operator => failure
        op_user = User.objects.get(username=data["username"])
        op_user.is_active = False
        op_user.save()

        self.assert_unauthorised_response(data, '{"error": "account_disabled"}')

    def test_inactive_provider_failure(self):
        # active specialist => success
        data = self.get_provider_data()
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

        # inactive specialist => failure
        sp_user = User.objects.get(username=data["username"])
        sp_user.is_active = False
        sp_user.save()

        self.assert_unauthorised_response(data, '{"error": "account_disabled"}')

    def test_username_does_not_exist(self):
        unlinked_username = "unknown"
        User.objects.create_user(unlinked_username, self.staff_email, self.staff_password)

        data = self.get_provider_data(username=unlinked_username)

        self.assert_unauthorised_response(data, self.INVALID_GRANT_ERROR)

    def test_user_does_not_exist(self):
        data = self.get_provider_data(username="user-does-not-exist")

        self.assert_unauthorised_response(data, self.INVALID_CLIENT_ERROR)

    def assert_unauthorised_response(self, data, expected_error):
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, expected_error)

    def test_operator_not_found_for_user(self):
        """Test operator user with no associated Operator model"""
        # Create a user without an associated Operator
        orphan_user = User.objects.create_user("orphan_op", "orphan@test.com", "password")

        # Create application for this orphan user
        Application.objects.create(
            user=orphan_user,
            name="operator",
            client_type=0,
            client_id="orphan_client",
            client_secret="secret",
            redirect_uris="http://localhost/redirect",
            authorization_grant_type="password",
        )

        data = {
            "client_id": "orphan_client",
            "client_secret": "secret",
            "grant_type": "password",
            "username": "orphan_op",
            "password": "password",
        }

        # This should fail because user exists but has no Operator model
        self.assert_unauthorised_response(data, self.INVALID_GRANT_ERROR)

    def test_staff_not_found_for_user(self):
        """Test staff user with no associated Staff model"""
        # Create a user without an associated Staff
        orphan_user = User.objects.create_user("orphan_staff", "orphan@test.com", "password")

        # Create application for this orphan user
        Application.objects.create(
            user=orphan_user,
            name="staff",
            client_type=0,
            client_id="orphan_staff_client",
            client_secret="secret",
            redirect_uris="http://localhost/redirect",
            authorization_grant_type="password",
        )

        data = {
            "client_id": "orphan_staff_client",
            "client_secret": "secret",
            "grant_type": "password",
            "username": "orphan_staff",
            "password": "password",
        }

        # This should fail because user exists but has no Staff model
        self.assert_unauthorised_response(data, self.INVALID_GRANT_ERROR)

    @mock.patch("cla_auth.views.logger")
    def test_user_data_retrieval_with_missing_operator(self, mock_logger):
        """Test _get_operator_data when Operator.DoesNotExist is raised"""
        from cla_auth.views import AccessTokenView

        view = AccessTokenView()
        orphan_user = User.objects.create_user("test_user", "test@example.com", "password")

        # This should trigger the Operator.DoesNotExist exception
        result = view._get_operator_data(orphan_user)

        self.assertIsNone(result)
        mock_logger.warning.assert_called_once_with("Operator not found for user", extra={"username": "test_user"})

    @mock.patch("cla_auth.views.logger")
    def test_user_data_retrieval_with_missing_staff(self, mock_logger):
        """Test _get_staff_data when Staff.DoesNotExist is raised"""
        from cla_auth.views import AccessTokenView

        view = AccessTokenView()
        orphan_user = User.objects.create_user("test_staff_user", "test@example.com", "password")

        # This should trigger the Staff.DoesNotExist exception
        result = view._get_staff_data(orphan_user)

        self.assertIsNone(result)
        mock_logger.warning.assert_called_once_with("Staff not found for user", extra={"username": "test_staff_user"})

    @mock.patch("cla_auth.views.logger")
    def test_add_user_details_error_handling(self, mock_logger):
        """Test error handling in add_user_details_to_response"""
        from cla_auth.views import AccessTokenView
        from django.http import HttpResponse

        view = AccessTokenView()

        # Create a mock request with invalid data
        class MockRequest:
            def __init__(self):
                self.POST = {"username": "nonexistent", "client_id": "invalid"}

        request = MockRequest()
        response = HttpResponse('{"access_token": "test"}', content_type="application/json")

        # This should trigger exception handling and log error
        result = view.add_user_details_to_response(request, response)

        # Should return original response when error occurs
        self.assertEqual(result, response)
        # Should log an error
        mock_logger.error.assert_called_once()

    def test_add_user_details_no_username(self):
        """Test add_user_details_to_response with no username"""
        from cla_auth.views import AccessTokenView
        from django.http import HttpResponse

        view = AccessTokenView()

        class MockRequest:
            def __init__(self):
                self.POST = {}  # No username

        request = MockRequest()
        response = HttpResponse('{"access_token": "test"}', content_type="application/json")

        with mock.patch("cla_auth.views.logger") as mock_logger:
            result = view.add_user_details_to_response(request, response)

            # Should return original response
            self.assertEqual(result, response)
            # Should log warning about no username
            mock_logger.warning.assert_called_once_with("No username found in request")

    @mock.patch("cla_auth.views.logger")
    def test_add_user_details_no_user_data_returned(self, mock_logger):
        """Test add_user_details_to_response when no user data is returned"""
        from cla_auth.views import AccessTokenView
        from django.http import HttpResponse

        view = AccessTokenView()

        # Create user and client but no associated Staff/Operator
        User.objects.create_user("orphan_user", "test@example.com", "password")
        Application.objects.create(
            name="staff",  # This will try to get Staff data
            client_type=0,
            client_id="test_client",
            client_secret="secret",
            redirect_uris="http://localhost/redirect",
            authorization_grant_type="password",
        )

        class MockRequest:
            def __init__(self):
                self.POST = {"username": "orphan_user", "client_id": "test_client"}

        request = MockRequest()
        response = HttpResponse('{"access_token": "test"}', content_type="application/json")

        result = view.add_user_details_to_response(request, response)

        # Should return original response without user data
        self.assertEqual(result, response)
        # Should log warning about no user data returned
        mock_logger.warning.assert_called_with(
            "No user data returned", extra={"username": "orphan_user", "client_name": "staff"}
        )

    @mock.patch("cla_auth.views.logger")
    def test_add_user_details_successful_logging(self, mock_logger):
        """Test successful logging in add_user_details_to_response"""
        # Test with the existing operator setup
        response = self.client.post(self.url, data=self.get_operator_data())
        self.assertEqual(response.status_code, 200)

        # Verify the logging calls were made
        mock_logger.info.assert_any_call(
            "Getting user data for authentication", extra={"client_name": "operator", "username": "operator"}
        )
        mock_logger.info.assert_any_call("Successfully added user details to response")


class MinimalCoverageTestCase(TestCase):
    """Minimal tests to cover specific uncovered lines"""

    def test_line_194_196_operator_does_not_exist(self):
        """Cover lines 194-196: Operator.DoesNotExist exception"""
        from cla_auth.views import AccessTokenView

        view = AccessTokenView()
        user = User.objects.create_user("test", "test@test.com", "pass")

        with mock.patch("cla_auth.views.logger") as mock_logger:
            result = view._get_operator_data(user)
            self.assertIsNone(result)
            mock_logger.warning.assert_called_once()

    def test_line_210_212_staff_does_not_exist(self):
        """Cover lines 210-212: Staff.DoesNotExist exception"""
        from cla_auth.views import AccessTokenView

        view = AccessTokenView()
        user = User.objects.create_user("test2", "test2@test.com", "pass")

        with mock.patch("cla_auth.views.logger") as mock_logger:
            result = view._get_staff_data(user)
            self.assertIsNone(result)
            mock_logger.warning.assert_called_once()

    def test_line_222_unknown_client_type(self):
        """Cover line 222: return None for unknown client type"""
        from cla_auth.views import AccessTokenView

        view = AccessTokenView()
        user = User.objects.create_user("test3", "test3@test.com", "pass")

        result = view._get_user_data_by_client_type(user, "unknown_client")
        self.assertIsNone(result)

    def test_line_232_233_no_username(self):
        """Cover lines 232-233: no username in request"""
        from cla_auth.views import AccessTokenView
        from django.http import HttpResponse

        view = AccessTokenView()

        class MockRequest:
            POST = {}  # No username

        request = MockRequest()
        response = HttpResponse("{}")

        with mock.patch("cla_auth.views.logger") as mock_logger:
            result = view.add_user_details_to_response(request, response)
            self.assertEqual(result, response)
            mock_logger.warning.assert_called_once_with("No username found in request")

    def test_line_244_245_no_user_data(self):
        """Cover lines 244-245: no user data returned"""
        from cla_auth.views import AccessTokenView
        from django.http import HttpResponse
        from oauth2_provider.models import Application

        view = AccessTokenView()
        User.objects.create_user("test4", "test4@test.com", "pass")
        Application.objects.create(
            name="unknown",
            client_id="test_client",
            client_secret="secret",
            client_type=0,
            authorization_grant_type="password",
        )

        class MockRequest:
            POST = {"username": "test4", "client_id": "test_client"}

        request = MockRequest()
        response = HttpResponse("{}")

        with mock.patch("cla_auth.views.logger") as mock_logger:
            result = view.add_user_details_to_response(request, response)
            self.assertEqual(result, response)
            mock_logger.warning.assert_called_with(
                "No user data returned", extra={"username": "test4", "client_name": "unknown"}
            )

    def test_line_258_260_exception_in_add_user_details(self):
        """Cover lines 258-260: Exception handling in add_user_details_to_response"""
        from cla_auth.views import AccessTokenView
        from django.http import HttpResponse

        view = AccessTokenView()

        class MockRequest:
            POST = {"username": "nonexistent", "client_id": "invalid"}

        request = MockRequest()
        response = HttpResponse("{}")

        with mock.patch("cla_auth.views.logger") as mock_logger:
            result = view.add_user_details_to_response(request, response)
            self.assertEqual(result, response)
            mock_logger.error.assert_called_once_with(
                "Error adding user details to response", exc_info=True, extra={"error": mock.ANY}
            )
