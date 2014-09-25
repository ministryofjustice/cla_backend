from rest_framework import status
from rest_framework.test import APITestCase

from core.tests.mommy_utils import make_recipe
from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from legalaid.tests.views.mixins.user_api import UserAPIMixin


class UserTests(CLAProviderAuthBaseApiTestMixin, UserAPIMixin, APITestCase):
    def assertUserEqual(self, data):
        _data = data.copy()
        del _data['provider']['id']

        self.assertDictContainsSubset({
            'username': u'john',
            'first_name': u'',
            'last_name': u'',
            'email': u'lennon@thebeatles.com',
            'provider': {'name': u'Name1'},
            'is_manager': False
        }, data)
        self.assertTrue('last_login' in data)
        self.assertTrue('created' in data)
        self.assertTrue('provider' in data)

    def get_other_users(self):
        return make_recipe('cla_provider.staff', _quantity=3)

    def get_organisation_users(self):
        return make_recipe('cla_provider.staff', provider=self.provider, _quantity=3)

    def test_manager_can_list_organisation_users(self):
        response = super(UserTests, self).test_manager_can_list_organisation_users()
        self.assertSetEqual({x['provider']['id'] for x in response.data}, {self.provider.id})

    def test_created_user_is_of_same_provider(self):
        data = {
            'password': 'foobarbaz1234567890',
            'username': 'cooldude',
            'first_name': 'elton',
            'last_name': 'john',
            'email': 'example@example.com'

        }

        response = self.client.post(
            self.list_url,
            data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('provider' in response.data.keys())
        self.assertEqual(response.data['provider']['id'], self.provider.id)

    def test_get_different_user_of_other_provider_not_allowed_as_manager(self):
        other_user = self.other_users[0]
        detail_url = self.get_user_detail_url(other_user.user.username)
        response = self.client.get(
            detail_url,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertNotEqual(self.provider, other_user.provider)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_cant_reset_password_of_other_provider_user(self):
        other_organisation_user = self.other_users[0]
        reset_url = self.get_user_password_reset_url(other_organisation_user.user.username)
        response = self.client.post(
            reset_url,
            {
                'new_password': 'b'*10
            },
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rest_password_my_organisation_user(self):
        organisation_user = self.get_organisation_users()[0].user
        reset_url = self.get_user_password_reset_url(organisation_user.username)
        response = self.client.post(
            reset_url,
            {
                'new_password': 'b'*10
            },
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

