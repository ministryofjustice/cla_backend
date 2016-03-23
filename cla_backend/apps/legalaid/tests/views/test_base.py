import datetime
from django.contrib.auth.models import User

from provider.oauth2.models import Client, AccessToken

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import CLABaseApiTestMixin

from cla_provider.models import Staff
from call_centre.models import Operator
from rest_framework import status


class CLAAuthBaseApiTestMixin(CLABaseApiTestMixin):
    """
    Useful testing methods

    NOTE: never subclass this directly, use one of the sublasses:
        CLAProviderAuthBaseApiTestMixin
        CLAOperatorAuthBaseApiTestMixin
        CLACheckerAuthBaseApiTestMixin

        instead.
    """
    DEFAULT_TOKEN = None

    def setUp(self):
        # create a user
        self.username = 'john'
        self.email = 'lennon@thebeatles.com'
        self.password = 'password'
        self.user = User.objects.create_user(self.username, self.email, self.password)

        # create a user
        self.mgr_username = 'sir_john'
        self.mgr_email = 'lemmings@thebeatles.com'
        self.mgr_password = 'password1'
        self.mgr_user = User.objects.create_user(self.mgr_username, self.mgr_email, self.mgr_password)

        # create an operator API client
        self.operator_api_client = Client.objects.create(
            user=self.user,
            name='operator',
            client_type=0,
            client_id='call_centre',
            client_secret='secret',
            url='http://localhost/',
            redirect_uri='http://localhost/redirect'
        )

        # create an staff API client
        self.staff_api_client = Client.objects.create(
            user=self.user,
            name='staff',
            client_type=0,
            client_id='cla_provider',
            client_secret='secret',
            url='http://provider.localhost/',
            redirect_uri='http://provider.localhost/redirect'
        )

        # create provider and staff user
        self.provider = make_recipe('cla_provider.provider')
        self.provider.staff_set.add(Staff(user=self.user))
        self.provider.staff_set.add(Staff(user=self.mgr_user, is_manager=True))
        self.provider.save()

        # create operator user
        self.operator = Operator.objects.create(user=self.user)
        self.operator_manager = Operator.objects.create(user=self.mgr_user, is_manager=True)

        # Expire token in the future when this codebase will be obsolete
        self.token_expires = datetime.datetime(2100, 1, 1, 0, 0, 0)

        # Create an access token
        self.operator_token = AccessToken.objects.create(
            user=self.user,
            client=self.operator_api_client,
            token='operator_token',
            scope=0,
            expires=self.token_expires
        )

        self.operator_manager_token = AccessToken.objects.create(
            user=self.mgr_user,
            client=self.operator_api_client,
            token='operator_manager_token',
            scope=0,
            expires=self.token_expires
        )
        # Create an access token
        self.staff_token = AccessToken.objects.create(
            user=self.user,
            client=self.staff_api_client,
            token='stafF_token',
            scope=0,
            expires=self.token_expires
        )

        self.staff_manager_token = AccessToken.objects.create(
            user=self.mgr_user,
            client=self.staff_api_client,
            token='stafF_token_mgr',
            scope=0,
            expires=self.token_expires
        )

        # set default token
        self.token = getattr(self, self.DEFAULT_TOKEN)
        self.manager_token = getattr(self, self.DEFAULT_MANAGER_TOKEN)
        self.invalid_token = getattr(self, self.INVALID_TOKEN)

        super(CLAAuthBaseApiTestMixin, self).setUp()

    def get_http_authorization(self, token=None):
        return super(CLAAuthBaseApiTestMixin, self).get_http_authorization(
            token or self.token
        )


class CLAProviderAuthBaseApiTestMixin(CLAAuthBaseApiTestMixin):
    DEFAULT_TOKEN = 'staff_token'
    DEFAULT_MANAGER_TOKEN = 'staff_manager_token'
    INVALID_TOKEN = 'operator_token'
    API_URL_NAMESPACE = 'cla_provider'
    OTHER_USER_ACCESS_STATUS_CODE = status.HTTP_404_NOT_FOUND


class CLAOperatorAuthBaseApiTestMixin(CLAAuthBaseApiTestMixin):
    DEFAULT_TOKEN = 'operator_token'
    DEFAULT_MANAGER_TOKEN = 'operator_manager_token'
    INVALID_TOKEN = 'staff_token'
    API_URL_NAMESPACE = 'call_centre'
    OTHER_USER_ACCESS_STATUS_CODE = status.HTTP_403_FORBIDDEN


class CLACheckerAuthBaseApiTestMixin(CLABaseApiTestMixin):
    API_URL_NAMESPACE = 'checker'
