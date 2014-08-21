from rest_framework.test import APITestCase

from core.tests.mommy_utils import make_recipe
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin

from legalaid.tests.views.mixins.user_api import UserAPIMixin


class UserTests(CLAOperatorAuthBaseApiTestMixin, UserAPIMixin, APITestCase):
    def assertUserEqual(self, data):
        self.assertDictEqual(data, {
            'username': u'john',
            'first_name': u'',
            'last_name': u'',
            'email': u'lennon@thebeatles.com',
            'is_manager': False
        })

    def get_other_users(self):
        return make_recipe('call_centre.operator', _quantity=3)
