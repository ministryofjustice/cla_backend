# coding=utf-8
from __future__ import unicode_literals

from rest_framework.test import APITestCase
from rest_framework import status

from core.tests.mommy_utils import make_recipe
from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from cla_provider.tests.mixins import ProviderAPIMixin


class ProviderAPITestCase(ProviderAPIMixin, CLAProviderAuthBaseApiTestMixin, APITestCase):
    """Test case for Provider API endpoint"""

    def make_resource(self, **kwargs):
        """Override to return the provider associated with the logged in user"""
        return self.provider

    # SECURITY TESTS

    def test_cannot_access_other_provider(self):
        """Test that a provider cannot access another provider's details"""
        # Create another provider
        other_provider = make_recipe("cla_provider.provider")

        url = self.get_detail_url(other_provider.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_only_own_provider_in_list(self):
        """Test that provider can only see their own provider in the list"""
        # Create another provider
        make_recipe("cla_provider.provider")

        response = self.client.get(self.list_url, HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.provider.id)

    # EDGE CASE TESTS

    def test_provider_with_no_categories(self):
        """Test provider with no contracted categories returns empty list"""
        # Remove all categories
        self.resource.law_category.clear()

        response = self.client.get(self.detail_url, HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["law_category"], [])

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied"""
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
