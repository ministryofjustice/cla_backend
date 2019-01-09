from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from legalaid.tests.views.mixins.third_party_api import ThirdPartyDetailsApiMixin


class ThirdPartyDetailsTestCase(CLAOperatorAuthBaseApiTestMixin, ThirdPartyDetailsApiMixin, APITestCase):
    pass
