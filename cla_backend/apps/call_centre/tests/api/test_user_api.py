from rest_framework import status
from rest_framework.test import APITestCase

from core.tests.mommy_utils import make_recipe
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin

from legalaid.tests.views.mixins.user_api import UserAPIMixin


class UserTests(CLAOperatorAuthBaseApiTestMixin, UserAPIMixin, APITestCase):
    def assertUserEqual(self, data):
        self.assertDictContainsSubset({
            'username': u'john',
            'first_name': u'',
            'last_name': u'',
            'email': u'lennon@thebeatles.com',
            'is_manager': False,
        }, data)
        self.assertTrue('last_login' in data)
        self.assertTrue('created' in data)

    def get_other_users(self):
        return make_recipe('call_centre.operator', _quantity=3)


    def test_rest_password_other_user_as_manager(self):
        other_user = self.other_users[0].user
        reset_url = self.get_user_password_reset_url(other_user.username)
        response = self.client.post(
            reset_url,
            {
                'new_password': 'b'*10
            },
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
