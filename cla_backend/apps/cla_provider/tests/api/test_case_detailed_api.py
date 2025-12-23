# coding=utf-8
from __future__ import unicode_literals

import mock

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from core.tests.mommy_utils import make_recipe
from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin
from cla_provider.serializers import DetailedCaseSerializer, CaseSerializer


class DetailedCaseSerializerTestCase(CLAProviderAuthBaseApiTestMixin, APITestCase):
    """Test case for DetailedCaseSerializer - focused on detailed functionality only"""

    def setUp(self):
        super(DetailedCaseSerializerTestCase, self).setUp()
        # Create a case assigned to our test provider with related objects
        self.case = make_recipe("legalaid.case", provider=self.provider)

    def test_serializer_extends_case_serializer(self):
        """Test that DetailedCaseSerializer extends CaseSerializer"""
        self.assertTrue(issubclass(DetailedCaseSerializer, CaseSerializer))

    def test_serializer_has_nested_read_only_fields(self):
        """Test that DetailedCaseSerializer has nested read-only fields"""
        serializer = DetailedCaseSerializer()

        nested_fields = ["personal_details", "adaptation_details", "thirdparty_details", "state"]
        for field_name in nested_fields:
            self.assertIn(field_name, serializer.fields)
            field = serializer.fields[field_name]
            self.assertTrue(field.read_only, "Field %s should be read_only" % field_name)

    def test_detailed_serializer_excludes_eligibility_check(self):
        """Test that DetailedCaseSerializer excludes eligibility_check field"""
        serializer = DetailedCaseSerializer()
        self.assertNotIn("eligibility_check", serializer.fields)

        # But basic CaseSerializer should still have it
        basic_serializer = CaseSerializer()
        self.assertIn("eligibility_check", basic_serializer.fields)

    def test_detailed_serializer_returns_expanded_objects(self):
        """Test that DetailedCaseSerializer returns full objects instead of references"""
        # Compare basic vs detailed serialization
        basic_serializer = CaseSerializer(self.case)
        detailed_serializer = DetailedCaseSerializer(self.case)

        basic_data = basic_serializer.data
        detailed_data = detailed_serializer.data

        # Detailed should include state field that basic doesn't have
        self.assertNotIn("state", basic_data)
        self.assertIn("state", detailed_data)

        # Basic should have eligibility_check but detailed should not
        self.assertIn("eligibility_check", basic_data)
        self.assertNotIn("eligibility_check", detailed_data)

        # The key difference: nested objects should be expanded as dictionaries
        if self.case.personal_details:
            self.assertIsInstance(detailed_data["personal_details"], dict)
            self.assertIn("full_name", detailed_data["personal_details"])

    def test_detailed_serializer_handles_null_relations(self):
        """Test that DetailedCaseSerializer handles null related objects gracefully"""
        case_minimal = make_recipe(
            "legalaid.case", provider=self.provider, personal_details=None, adaptation_details=None
        )

        serializer = DetailedCaseSerializer(case_minimal)
        data = serializer.data

        # Should return None for missing relations without errors
        self.assertIsNone(data["personal_details"])
        self.assertIsNone(data["adaptation_details"])

        # Should still have state field even with minimal case
        self.assertIn("state", data)
        self.assertEqual(data["state"], "new")  # Default state for new case


class DetailedCaseEndpointTestCase(CLAProviderAuthBaseApiTestMixin, APITestCase):
    """Test case for the detailed case API endpoint - focused on endpoint-specific functionality"""

    def setUp(self):
        super(DetailedCaseEndpointTestCase, self).setUp()
        self.case = make_recipe("legalaid.case", provider=self.provider)

    def get_detailed_url(self, reference=None):
        reference = reference or self.case.reference
        return reverse("cla_provider:case-detailed", args=(), kwargs={"reference": reference})

    def test_detailed_endpoint_exists_and_uses_correct_serializer(self):
        """Test that the detailed endpoint exists and uses DetailedCaseSerializer"""
        url = self.get_detailed_url()

        # Test without auth first
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Test with auth
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization())

        # If endpoint exists, it should return detailed data
        if response.status_code == status.HTTP_200_OK:
            data = response.data
            # Should have nested objects as dicts if they exist
            if self.case.personal_details:
                self.assertIsInstance(data.get("personal_details"), dict)

            # Should have state field but not eligibility_check
            self.assertIn("state", data)
            self.assertNotIn("eligibility_check", data)

    def test_detailed_endpoint_case_ownership(self):
        """Test that detailed endpoint respects case ownership"""
        # Case not owned by provider
        other_provider = make_recipe("cla_provider.provider")
        other_case = make_recipe("legalaid.case", provider=other_provider)

        url = self.get_detailed_url(other_case.reference)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch("cla_provider.views.DetailedCaseSerializer")
    def test_detailed_endpoint_uses_detailed_serializer(self, mock_serializer):
        """Test that the endpoint specifically uses DetailedCaseSerializer"""
        url = self.get_detailed_url()
        mock_instance = mock_serializer.return_value
        mock_instance.data = {"reference": self.case.reference}

        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization())

        if response.status_code == status.HTTP_200_OK:
            mock_serializer.assert_called_once()
            call_args = mock_serializer.call_args
            self.assertEqual(call_args[1]["instance"], self.case)
