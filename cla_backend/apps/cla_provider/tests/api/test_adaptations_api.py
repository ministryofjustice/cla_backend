from core.tests.test_base import CLAProviderAuthBaseApiTestMixin
from rest_framework.test import APITestCase

from legalaid.tests.views.mixins.adaptations_api import \
    AdaptationsMetadataAPIMixin


class AdaptationsMetadataTestCase(
    CLAProviderAuthBaseApiTestMixin, AdaptationsMetadataAPIMixin,
    APITestCase
):
    API_URL_NAMESPACE = 'cla_provider'
