from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin

from rest_framework.test import APITestCase

from legalaid.tests.views.mixins.third_party_api import \
    ThirdPartyDetailsApiMixin


class ThirdPartyDetailsTestCase(
    CLAOperatorAuthBaseApiTestMixin, ThirdPartyDetailsApiMixin, APITestCase
):

    def get_http_authorization(self):
        return 'Bearer %s' % self.token