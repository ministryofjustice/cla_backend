from django.contrib.auth.models import User

from provider.oauth2.models import Client, AccessToken

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import CLABaseApiTestMixin

from cla_provider.models import Staff
from call_centre.models import Operator


class CLAAuthBaseApiTestMixin(CLABaseApiTestMixin):
    """
    Useful testing methods
    """
    DEFAULT_TOKEN = None

    def setUp(self):
        super(CLAAuthBaseApiTestMixin, self).setUp()

        # create a user
        self.username = 'john'
        self.email = 'lennon@thebeatles.com'
        self.password = 'password'
        self.user = User.objects.create_user(self.username, self.email, self.password)

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
        self.provider.save()

        # create operator user
        self.operator = Operator.objects.create(user=self.user)

        # Create an access token
        self.operator_token = AccessToken.objects.create(
            user=self.user,
            client=self.operator_api_client,
            token='operator_token',
            scope=0
        )

        # Create an access token
        self.staff_token = AccessToken.objects.create(
            user=self.user,
            client=self.staff_api_client,
            token='stafF_token',
            scope=0
        )

        # set default token
        self.token = getattr(self, self.DEFAULT_TOKEN)
        self.invalid_token = getattr(self, self.INVALID_TOKEN)

    def get_http_authorization(self, token=None):
        return super(CLAAuthBaseApiTestMixin, self).get_http_authorization(
            token or self.token
        )


class CLAProviderAuthBaseApiTestMixin(CLAAuthBaseApiTestMixin):
    DEFAULT_TOKEN = 'staff_token'
    INVALID_TOKEN = 'operator_token'
    API_URL_NAMESPACE = 'cla_provider'


class CLAOperatorAuthBaseApiTestMixin(CLAAuthBaseApiTestMixin):
    DEFAULT_TOKEN = 'operator_token'
    INVALID_TOKEN = 'staff_token'
    API_URL_NAMESPACE = 'call_centre'


class CLACheckerAuthBaseApiTestMixin(CLABaseApiTestMixin):
    API_URL_NAMESPACE = 'checker'
