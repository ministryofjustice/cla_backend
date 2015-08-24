from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from legalaid.tests.views.mixins.adaptations_api import \
    AdaptationsMetadataAPIMixin, AdaptationsDetailsAPIMixin


class AdaptationsMetadataTestCase(
    CLAOperatorAuthBaseApiTestMixin, AdaptationsMetadataAPIMixin,
    APITestCase
):
    pass


class AdaptationsDetailsTestCase(
    CLAOperatorAuthBaseApiTestMixin, AdaptationsDetailsAPIMixin,
    APITestCase
):
    pass
