from rest_framework.test import APITestCase
from rest_framework import status

from core.tests.mommy_utils import make_recipe
from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from cla_common.constants import REQUIRES_ACTION_BY

from legalaid.tests.views.mixins.adaptations_api import \
    AdaptationsMetadataAPIMixin, AdaptationsDetailsAPIMixin


class AdaptationsMetadataTestCase(
    CLAProviderAuthBaseApiTestMixin, AdaptationsMetadataAPIMixin,
    APITestCase
):
    pass


class AdaptationsDetailsTestCase(
    CLAProviderAuthBaseApiTestMixin, AdaptationsDetailsAPIMixin,
    APITestCase
):

    def setUp(self):
        super(AdaptationsDetailsTestCase, self).setUp()

        self.check_case.provider = self.provider
        self.check_case.requires_action_by = REQUIRES_ACTION_BY.PROVIDER
        self.check_case.save()

    # SECURITY

    def test_get_not_found_if_not_belonging_to_provider(self):
        self.check_case.provider = None
        self.check_case.requires_action_by = REQUIRES_ACTION_BY.OPERATOR
        self.check_case.save()

        response = self.client.get(
            self.detail_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_not_found_if_belonging_to_different_provider(self):
        other_provider = make_recipe('cla_provider.provider')

        self.check_case.provider = other_provider
        self.check_case.save()

        response = self.client.get(
            self.detail_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
