from rest_framework import status
from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from legalaid.tests.views.mixins.eligibility_check_api import NestedEligibilityCheckAPIMixin


class EligibilityCheckTestCase(CLAOperatorAuthBaseApiTestMixin, NestedEligibilityCheckAPIMixin, APITestCase):
    LOOKUP_KEY = "case_reference"

    @property
    def response_keys(self):
        return [
            "reference",
            "category",
            "notes",
            "your_problem_notes",
            "property_set",
            "dependants_young",
            "dependants_old",
            "you",
            "partner",
            "disputed_savings",
            "has_partner",
            "on_passported_benefits",
            "on_nass_benefits",
            "is_you_or_your_partner_over_60",
            "state",
            "specific_benefits",
            "has_passported_proceedings_letter",
        ]

    def test_notes_are_readonly(self):
        data = {"notes": "just trying...", "your_problem_notes": "ipsum lorem2"}
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # checking the changed properties
        self.resource.your_problem_notes = data["your_problem_notes"]
        self.assertEligibilityCheckEqual(response.data, self.resource)
        self.assertTrue(response.data["notes"] != data["notes"])

    def test_empty_fields(self):
        """
        When patching a NullBooleanField setting it to None, DRF saves it
        as None value.
        """
        data = {
            "category": None,
            "dependants_old": None,
            "dependants_young": None,
            "has_partner": None,
            "is_you_or_your_partner_over_60": None,
            "notes": "",
            "on_nass_benefits": None,
            "on_passported_benefits": None,
            "partner": None,
            "property_set": [],
            "state": "unknown",
            "you": None,
            "disputed_savings": None,
            "your_problem_notes": "",
        }
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        # TODO: needs more checks

        self.assertEqual(response.data["has_partner"], None)
        self.assertEqual(response.data["is_you_or_your_partner_over_60"], None)

    def test_check_validate_api_method_works(self):
        # actual testing of 'validate' is done in model tests.
        response = self.client.get(
            self.detail_url + "validate/", {}, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"warnings": {}})
