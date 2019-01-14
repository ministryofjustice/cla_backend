import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.test import TestCase
from django.conf import settings
from django.utils import timezone
import mock

from provider.oauth2.models import Client
from core.tests.mommy_utils import make_recipe
from cla_provider.models import Staff
from call_centre.models import Operator
from cla_auth.models import AccessAttempt


class LoginTestCase(TestCase):
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
        self.prov.staff_set.add(Staff(user=self.staff_user))
        self.prov.save()

        # create an operator API client
        self.op_client = Client.objects.create(
            user=self.op_user,
            name="operator",
            client_type=0,
            client_id="call_centre",
            client_secret="secret",
            url="http://localhost/",
            redirect_uri="http://localhost/redirect",
        )

        # create an staff API client
        self.staff_api_client = Client.objects.create(
            user=self.staff_user,
            name="staff",
            client_type=0,
            client_id="cla_provider",
            client_secret="secret",
            url="http://provider.localhost/",
            redirect_uri="http://provider.localhost/redirect",
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

    def test_invalid_auth_settings(self):
        # invalid client_id
        response = self.client.post(self.url, data=self.get_operator_data(client_id="invalid"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"error": "invalid_client"}')

        # invalid client secret
        response = self.client.post(self.url, data=self.get_operator_data(client_secret="invalid"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"error": "invalid_client"}')

    def test_operator_success(self):
        response = self.client.post(self.url, data=self.get_operator_data())
        self.assertEqual(response.status_code, 200)

    def test_operator_invalid_password(self):
        response = self.client.post(self.url, data=self.get_operator_data(password="invalid"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"error": "invalid_grant"}')

    def test_staff_success(self):
        response = self.client.post(self.url, data=self.get_provider_data())

        self.assertEqual(response.status_code, 200)

    def test_staff_invalid_password(self):
        response = self.client.post(self.url, data=self.get_provider_data(password="invalid"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"error": "invalid_grant"}')

    def test_locks_user_out_after_n_attempts(self):
        self.assertEqual(AccessAttempt.objects.count(), 0)

        for index in range(settings.LOGIN_FAILURE_LIMIT):
            response = self.client.post(self.url, data=self.get_operator_data(password="invalid"))
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.content, '{"error": "invalid_grant"}')

        self.assertEqual(AccessAttempt.objects.count(), settings.LOGIN_FAILURE_LIMIT)

        # the n-th time, the user's account will be locked out
        response = self.client.post(self.url, data=self.get_operator_data(password="invalid"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"error": "locked_out"}')

        # from now on, even if the password is corrent, the account is locked
        response = self.client.post(self.url, data=self.get_operator_data())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"error": "locked_out"}')

        with mock.patch("cla_auth.forms.timezone") as mocked_timezone:
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

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"error": "account_disabled"}')

    def test_inactive_provider_failure(self):
        # active specialist => success
        data = self.get_provider_data()
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

        # inactive specialist => failure
        sp_user = User.objects.get(username=data["username"])
        sp_user.is_active = False
        sp_user.save()

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"error": "account_disabled"}')
