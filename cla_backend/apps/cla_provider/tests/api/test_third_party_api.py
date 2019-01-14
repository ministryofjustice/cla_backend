from rest_framework.test import APITestCase
from rest_framework import status

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin
from core.tests.mommy_utils import make_recipe

from cla_common.constants import REQUIRES_ACTION_BY

from legalaid.tests.views.mixins.third_party_api import ThirdPartyDetailsApiMixin


class ThirdPartyDetailsTestCase(CLAProviderAuthBaseApiTestMixin, ThirdPartyDetailsApiMixin, APITestCase):
    def make_parent_resource(self, **kwargs):
        kwargs.update({"provider": self.provider, "requires_action_by": REQUIRES_ACTION_BY.PROVIDER})
        return super(ThirdPartyDetailsTestCase, self).make_parent_resource(**kwargs)

    # SECURITY

    def test_get_not_found_if_not_belonging_to_provider(self):
        self.parent_resource.provider = None
        self.parent_resource.requires_action_by = REQUIRES_ACTION_BY.OPERATOR
        self.parent_resource.save()

        response = self.client.get(self.detail_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_not_found_if_belonging_to_different_provider(self):
        other_provider = make_recipe("cla_provider.provider")

        self.parent_resource.provider = other_provider
        self.parent_resource.save()

        response = self.client.get(self.detail_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
