import mock

from rest_framework.test import APITestCase
from rest_framework import status

from core.tests.mommy_utils import make_recipe
from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from cla_common.constants import REQUIRES_ACTION_BY

from legalaid.tests.views.mixins.personal_details_api import PersonalDetailsAPIMixin


class PersonalDetailsTestCase(CLAProviderAuthBaseApiTestMixin, PersonalDetailsAPIMixin, APITestCase):
    def make_parent_resource(self, **kwargs):
        kwargs.update({"provider": self.provider, "requires_action_by": REQUIRES_ACTION_BY.PROVIDER})
        return super(PersonalDetailsTestCase, self).make_parent_resource(**kwargs)

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

    # GET DIVERSITY

    @property
    def get_diversity_url(self):
        return self.get_detail_url(self.resource_lookup_value, suffix="get-diversity")

    @mock.patch("cla_provider.views._request_has_mcc_role", return_value=True)
    def test_get_diversity_empty_when_no_data(self, _mock_mcc):
        self.resource.diversity = None
        self.resource.save()

        response = self.client.get(self.get_diversity_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {"gender": None, "ethnicity": None, "disability": None})

    @mock.patch("cla_provider.views._request_has_mcc_role", return_value=True)
    def test_get_diversity_not_found_if_not_belonging_to_provider(self, _mock_mcc):
        self.parent_resource.provider = None
        self.parent_resource.requires_action_by = REQUIRES_ACTION_BY.OPERATOR
        self.parent_resource.save()

        response = self.client.get(self.get_diversity_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch("cla_provider.views._request_has_mcc_role", return_value=True)
    @mock.patch("cla_provider.views.diversity.load_diversity_data_for_mcc")
    def test_get_diversity_returns_decrypted_data(self, mocked_load, _mock_mcc):
        expected = {"gender": "MALE", "ethnicity": "WHITE", "disability": "NO"}
        mocked_load.return_value = expected

        self.resource.diversity = "encrypted-placeholder"
        self.resource.save()

        response = self.client.get(self.get_diversity_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertDictEqual(response.data, expected)
        mocked_load.assert_called_once_with(self.resource.pk)

    def test_get_diversity_returns_403_if_not_mcc(self):
        response = self.client.get(self.get_diversity_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
