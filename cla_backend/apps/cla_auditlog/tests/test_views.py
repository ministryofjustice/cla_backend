from rest_framework.test import APITestCase

from core.tests.test_base import SimpleResourceAPIMixin
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from call_centre.tests.api.test_case_api import BaseCaseTestCase
from complaints.tests.test_complaints_api import ComplaintTestMixin


class CaseViewSetTestCase(BaseCaseTestCase):
    def test_audit_log_multiple_case_views(self):
        count = self.resource.audit_log.count()
        self.client.get(self.detail_url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token)
        self.assertEqual(self.resource.audit_log.count(), count + 1)
        self.client.get(self.detail_url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token)
        self.assertEqual(self.resource.audit_log.count(), count + 2)


class ComplaintsViewSetTestCase(
    ComplaintTestMixin, CLAOperatorAuthBaseApiTestMixin, SimpleResourceAPIMixin, APITestCase
):
    def test_audit_log_multiple_complaint_views(self):
        count = self.resource.audit_log.count()
        self.client.get(self.detail_url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token)
        self.assertEqual(self.resource.audit_log.count(), count + 1)
        self.client.get(self.detail_url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token)
        self.assertEqual(self.resource.audit_log.count(), count + 2)
