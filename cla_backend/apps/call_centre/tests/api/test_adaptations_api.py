from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin
from rest_framework.test import APITestCase

from legalaid.tests.views.mixins.adaptations_api import \
    AdaptationsMetadataAPIMixin, AdaptationsDetailsAPIMixin


class AdaptationsMetadataTestCase(
    CLAOperatorAuthBaseApiTestMixin, AdaptationsMetadataAPIMixin,
    APITestCase
):
    API_URL_NAMESPACE = 'call_centre'


class AdaptationsDetailsTestCase(
    CLAOperatorAuthBaseApiTestMixin, AdaptationsDetailsAPIMixin,
    APITestCase
):

    def get_http_authorization(self):
        return 'Bearer %s' % self.token
