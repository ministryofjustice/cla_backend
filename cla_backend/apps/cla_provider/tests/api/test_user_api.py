from rest_framework.test import APITestCase

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import CLAProviderAuthBaseApiTestMixin

from legalaid.tests.views.mixins.user_api import UserAPIMixin


class UserTests(CLAProviderAuthBaseApiTestMixin, UserAPIMixin, APITestCase):
    def assertUserEqual(self, data):
        _data = data.copy()
        del _data['provider']['id']

        self.assertDictEqual(_data, {
            'username': u'john',
            'first_name': u'',
            'last_name': u'',
            'email': u'lennon@thebeatles.com',
            'provider': {'name': u'Name1'},
            'is_manager': False
        })

    def get_other_users(self):
        return make_recipe('cla_provider.staff', _quantity=3)
