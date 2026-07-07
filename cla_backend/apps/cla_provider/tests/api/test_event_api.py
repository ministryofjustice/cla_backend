from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status
import mock

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin
from cla_eventlog.tests.test_views import EventAPIMixin


class EventViewSetTestCase(CLAProviderAuthBaseApiTestMixin, EventAPIMixin, APITestCase):
    def get_event_key(self):
        return "accept_case"


class RejectCaseEventVisibilityTestCase(CLAProviderAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(RejectCaseEventVisibilityTestCase, self).setUp()
        self.reject_event_url = reverse("cla_provider:event-detail", args=(), kwargs={"action": "reject_case"})

    def test_non_mcc_users_do_not_see_mcc_only_reject_codes(self):
        response = self.client.get(
            self.reject_event_url,
            HTTP_AUTHORIZATION=self.get_http_authorization(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_codes = [item["code"] for item in response.data]
        self.assertNotIn("MERI", returned_codes)
        self.assertNotIn("DUPL", returned_codes)
        self.assertNotIn("CLOT", returned_codes)

    @mock.patch("cla_provider.views.EventViewSet._is_mcc_user", return_value=True)
    def test_mcc_users_see_mcc_only_reject_codes(self, _mock_is_mcc_user):
        response = self.client.get(
            self.reject_event_url,
            HTTP_AUTHORIZATION=self.get_http_authorization(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_codes = [item["code"] for item in response.data]
        self.assertIn("MERI", returned_codes)
        self.assertIn("DUPL", returned_codes)
        self.assertIn("CLOT", returned_codes)
