from django.contrib.auth.models import User
from provider.oauth2.models import Client, AccessToken

from rest_framework import status


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
    def setUp(self):
        # create a user
        self.username = 'john'
        self.email = 'lennon@thebeatles.com'
        self.password = 'password'
        self.user = User.objects.create_user(self.username, self.email, self.password)

        # create an API client
        self.api_client = Client.objects.create(
            user=self.user,
            name='operator',
            client_type=0,
            client_id='call_centre',
            client_secret='secret',
            url='http://localhost/',
            redirect_uri='http://localhost/redirect'
        )

        # Create an access token
        self.token = AccessToken.objects.create(
            user=self.user,
            client=self.api_client,
            token='token',
            scope=0
        )

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
