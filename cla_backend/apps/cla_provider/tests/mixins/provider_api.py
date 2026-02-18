from rest_framework import status

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin
from cla_provider.models import ProviderAllocation


class ProviderAPIMixin(SimpleResourceAPIMixin):
    LOOKUP_KEY = "pk"
    API_URL_BASE_NAME = "provider"
    RESOURCE_RECIPE = "cla_provider.provider"

    def setUp(self):
        super(ProviderAPIMixin, self).setUp()

        # Create some categories
        self.category1 = make_recipe("legalaid.category", code="debt", name="Debt")
        self.category2 = make_recipe("legalaid.category", code="housing", name="Housing")

        # Add categories to the provider using ProviderAllocation intermediary model
        ProviderAllocation.objects.create(
            provider=self.resource,
            category=self.category1,
            weighted_distribution=0.5
        )
        ProviderAllocation.objects.create(
            provider=self.resource,
            category=self.category2,
            weighted_distribution=0.5
        )

    def test_get_allowed(self):
        """
        Ensure we can GET the detail endpoint and it returns provider with categories
        """
        # DETAIL
        response = self.client.get(self.detail_url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check provider fields
        self.assertEqual(response.data["id"], self.resource.id)
        self.assertEqual(response.data["name"], self.resource.name)

        # Check law_category is present
        self.assertIn("law_category", response.data)
        self.assertEqual(len(response.data["law_category"]), 2)

        # Check category codes
        category_codes = [cat["code"] for cat in response.data["law_category"]]
        self.assertIn("debt", category_codes)
        self.assertIn("housing", category_codes)

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE (read-only endpoint)
        """
        # LIST
        self._test_post_not_allowed(self.list_url)
        self._test_put_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.list_url)

        # DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_put_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)

    def test_category_fields_structure(self):
        """
        Test that category fields contain expected information
        """
        response = self.client.get(self.detail_url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check each category has required fields
        for category in response.data["law_category"]:
            self.assertIn("code", category)
            self.assertIn("name", category)
            self.assertIn("description", category)
