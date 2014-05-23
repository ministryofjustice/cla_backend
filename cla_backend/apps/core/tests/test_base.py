from django.contrib.auth.models import User

from rest_framework import status

from provider.oauth2.models import Client, AccessToken
from core.tests.mommy_utils import make_recipe

from cla_provider.models import Staff
from call_centre.models import Operator


class CLABaseApiTestMixin(object):
    """
    Useful testing methods
    """
    def _test_get_not_allowed(self, url):
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_post_not_allowed(self, url, data={}):
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_put_not_allowed(self, url, data={}):
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_delete_not_allowed(self, url):
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)



class CLAAuthBaseApiTestMixin(object):
    """
    Useful testing methods
    """
    DEFAULT_TOKEN = None

    def setUp(self):
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
        Operator.objects.create(user=self.user)

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

    def _test_get_not_allowed(self, url):
        response = self.client.get(url,
                                   HTTP_AUTHORIZATION="Bearer %s" % self.token,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_post_not_allowed(self, url, data={}):
        response = self.client.post(url, data,
                                    HTTP_AUTHORIZATION="Bearer %s" % self.token,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_put_not_allowed(self, url, data={}):
        response = self.client.put(url, data,
                                   HTTP_AUTHORIZATION="Bearer %s" % self.token,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_delete_not_allowed(self, url):
        response = self.client.delete(url,
                                      HTTP_AUTHORIZATION="Bearer %s" % self.token,
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_patch_not_allowed(self, url):
        response = self.client.patch(url,
                                      HTTP_AUTHORIZATION="Bearer %s" % self.token,
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def _test_get_not_authorized(self, url, token):
        response = self.client.get(url,
                                   HTTP_AUTHORIZATION="Bearer %s" % token,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_post_not_authorized(self, url, token, data={}):
        response = self.client.post(url, data,
                                    HTTP_AUTHORIZATION="Bearer %s" % token,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_put_not_authorized(self, url, token, data={}):
        response = self.client.put(url, data,
                                   HTTP_AUTHORIZATION="Bearer %s" % token,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_delete_not_authorized(self, url, token):
        response = self.client.delete(url,
                                      HTTP_AUTHORIZATION="Bearer %s" % token,
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_patch_not_authorized(self, url, token):
        response = self.client.patch(url,
                                     HTTP_AUTHORIZATION="Bearer %s" % token,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CLAProviderAuthBaseApiTestMixin(CLAAuthBaseApiTestMixin):
    DEFAULT_TOKEN = 'staff_token'

class CLAOperatorAuthBaseApiTestMixin(CLAAuthBaseApiTestMixin):
    DEFAULT_TOKEN = 'operator_token'

