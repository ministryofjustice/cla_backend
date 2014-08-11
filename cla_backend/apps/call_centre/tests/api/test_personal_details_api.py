from rest_framework.test import APITestCase

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin

from legalaid.tests.views.mixins.personal_details_api import \
    PersonalDetailsAPIMixin


class PersonalDetailsTestCase(
    CLAOperatorAuthBaseApiTestMixin, PersonalDetailsAPIMixin, APITestCase
):

    def get_http_authorization(self):
        return 'Bearer %s' % self.token
