from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin
from rest_framework.test import APITestCase

from legalaid.tests.views.mixins.adaptations_api import \
    AdaptationsMetadataAPIMixin


class AdaptationsMetadataTestCase(
    CLAOperatorAuthBaseApiTestMixin, AdaptationsMetadataAPIMixin,
    APITestCase
):
    API_URL_NAMESPACE = 'call_centre'
