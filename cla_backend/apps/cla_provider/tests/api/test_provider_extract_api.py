from mock import patch
from lxml import objectify
from django.core.urlresolvers import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from cla_common.constants import REQUIRES_ACTION_BY
from core.tests.mommy_utils import make_recipe

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from legalaid.tests.views.mixins.provider_extract_api import ProviderExtractAPIMixin

from cla_auth.constants import PROVIDER_ROLE
from cla_auth.tests.test_authentication import EntraTokenGeneratorMixin


class ProviderExtractTests(CLAProviderAuthBaseApiTestMixin, ProviderExtractAPIMixin, APITestCase):
    def test_contents_is_xmlish(self):
        """
        The extract we're copying isn't valid XML but we can still check that the
        extract we're sending is somewhat valid XML.
        """

        response = self.client.post(self.detail_url, data=self.get_valid_post_data(CHSCRN=self.case.reference))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        o = objectify.fromstring(response.content)

        self.assertListEqual(o.attrib.keys(), ["CRN", "CaseCreated"])


class ProviderExtractEntraTests(EntraTokenGeneratorMixin, APITestCase):
    """
    Covers the ProviderExtractEntraForm path: Entra-authenticated providers only
    need to send CHSCRN, none of the legacy CHS credential fields.
    """

    FIRM_NAME = "THE FIRM NAME LTD"

    def setUp(self):
        super(ProviderExtractEntraTests, self).setUp()

        self.settings_override = self.settings(
            ENTRA_TENANT_ID="test-tenant-id", ENTRA_EXPECTED_AUDIENCE="test-audience"
        )
        self.settings_override.enable()

        self.public_keys_patcher = patch("cla_auth.authentication.EntraAccessTokenAuthentication._public_keys")
        self.public_keys_mock = self.public_keys_patcher.start()
        self.public_keys_mock.return_value = self.mock_jwks["keys"]

        self.provider = make_recipe("cla_provider.provider", name=self.FIRM_NAME, active=True)
        self.case = make_recipe(
            "legalaid.case", provider=self.provider, requires_action_by=REQUIRES_ACTION_BY.PROVIDER
        )
        self.detail_url = reverse("cla_provider:provider-extract")

    def tearDown(self):
        self.public_keys_patcher.stop()

    def auth_header(self, **token_kwargs):
        token_kwargs.setdefault("firm_name", self.FIRM_NAME)
        token_kwargs.setdefault("app_roles", PROVIDER_ROLE)
        # Use a distinct email from the mixin's default ("test@example.com").
        # The mixin creates a bare User with that email but no Staff link;
        # get_or_create_user would return it early, skipping _create_provider(),
        # leaving us with a user that fails IsProviderPermission.
        token_kwargs.setdefault("email", "new-provider-staff@example.com")
        token = self._create_token(**token_kwargs)
        return {"HTTP_AUTHORIZATION": "Bearer %s" % token}

    def test_valid_entra_post_returns_extract(self):
        response = self.client.post(
            self.detail_url, data={"CHSCRN": self.case.reference}, **self.auth_header()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        o = objectify.fromstring(response.content)
        self.assertEqual(o.attrib["CRN"], str(self.case.laa_reference))

    def test_entra_post_missing_chscrn_is_bad_request(self):
        response = self.client.post(self.detail_url, data={}, **self.auth_header())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_entra_post_unknown_crn_not_found(self):
        response = self.client.post(
            self.detail_url, data={"CHSCRN": "NONEXISTENT-CRN"}, **self.auth_header()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_entra_post_case_belongs_to_other_provider_is_forbidden(self):
        other_provider = make_recipe("cla_provider.provider", name="OTHER FIRM LTD", active=True)
        other_case = make_recipe(
            "legalaid.case", provider=other_provider, requires_action_by=REQUIRES_ACTION_BY.PROVIDER
        )
        response = self.client.post(
            self.detail_url, data={"CHSCRN": other_case.reference}, **self.auth_header()
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_is_xml_with_key_fields(self):
        response = self.client.post(
            self.detail_url, data={"CHSCRN": self.case.reference}, **self.auth_header()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/xml", response["Content-Type"])
        o = objectify.fromstring(response.content)
        self.assertIn("CRN", o.attrib)
        self.assertIn("CaseCreated", o.attrib)
        self.assertEqual(str(o.attrib["CRN"]), str(self.case.laa_reference))
        self.assertTrue(hasattr(o, "MeansTestResult"))
        self.assertTrue(hasattr(o, "ReferredOrganisation"))
        self.assertEqual(str(o.ReferredOrganisation.Organisation), self.FIRM_NAME)

    def test_entra_post_does_not_require_legacy_chs_fields(self):
        """No CHSOrganisationID/CHSUserName/CHSPassword needed for the Entra path."""
        response = self.client.post(
            self.detail_url, data={"CHSCRN": self.case.reference}, **self.auth_header()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(CORS_ORIGIN_WHITELIST=["https://allowed.example"])
    def test_options_with_allowed_origin_returns_cors_headers(self):
        response = self.client.options(self.detail_url, HTTP_ORIGIN="https://allowed.example")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Access-Control-Allow-Origin"], "https://allowed.example")

    @override_settings(CORS_ORIGIN_WHITELIST=["https://allowed.example"])
    def test_options_with_disallowed_origin_omits_cors_headers(self):
        response = self.client.options(self.detail_url, HTTP_ORIGIN="https://blocked.example")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("Access-Control-Allow-Origin", response)

    @override_settings(CORS_ORIGIN_WHITELIST=["https://allowed.example"])
    def test_post_with_allowed_origin_returns_cors_headers(self):
        response = self.client.post(
            self.detail_url,
            data={"CHSCRN": self.case.reference},
            HTTP_ORIGIN="https://allowed.example",
            **self.auth_header()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Access-Control-Allow-Origin"], "https://allowed.example")

    @override_settings(CORS_ORIGIN_WHITELIST=["https://allowed.example"])
    def test_post_with_disallowed_origin_omits_cors_headers(self):
        response = self.client.post(
            self.detail_url,
            data={"CHSCRN": self.case.reference},
            HTTP_ORIGIN="https://blocked.example",
            **self.auth_header()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("Access-Control-Allow-Origin", response)

    @override_settings(CORS_ORIGIN_WHITELIST=["https://allowed.example"], CORS_ALLOW_CREDENTIALS=True)
    def test_post_with_allowed_origin_includes_credentials_header_when_enabled(self):
        response = self.client.post(
            self.detail_url,
            data={"CHSCRN": self.case.reference},
            HTTP_ORIGIN="https://allowed.example",
            **self.auth_header()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Access-Control-Allow-Origin"], "https://allowed.example")
        self.assertEqual(response["Access-Control-Allow-Credentials"], "true")
