from django.test import TestCase
from django.core.urlresolvers import reverse

from core.tests.mommy_utils import make_recipe

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin


class CaseViewSetTestCase(CLAOperatorAuthBaseApiTestMixin, TestCase):
    def setUp(self):
        super(CaseViewSetTestCase, self).setUp()

    def test_audit_log_multiple_case_views(self):
        case = make_recipe("legalaid.case")
        url = reverse("call_centre:case-detail", args=(), kwargs={"reference": case.reference})
        self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token)
        self.assertEqual(case.audit_log.count(), 1)
        self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token)
        self.assertEqual(case.audit_log.count(), 2)
