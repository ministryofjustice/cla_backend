from django.test import TestCase
from django.core.urlresolvers import reverse

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin


class FullCaseViewSetTestCase(CLAOperatorAuthBaseApiTestMixin, TestCase):
    def setUp(self):
        super(FullCaseViewSetTestCase, self).setUp()
        self.url = reverse("call_centre:case-list")

    def test_search_unicode(self):
        response = self.client.get(
            self.url + "?search=Mark%20O%E2%80%99Brien", HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token
        )
        self.assertEqual(response.status_code, 200)

    def test_search_ascii(self):
        response = self.client.get(
            self.url + "?search=John%20Smith", HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token
        )
        self.assertEqual(response.status_code, 200)
