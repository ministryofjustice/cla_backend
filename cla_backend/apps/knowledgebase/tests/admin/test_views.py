from django.test import TestCase
from django.core.urlresolvers import reverse


class KnowledgebaseArticleAdminViewTestCase(TestCase):
    def test_csv_import_access_unathenticated_users(self):
        url = reverse("admin:knowledgebase_import_csv")
        response = self.client.get(url)
        expected_redirect_url = "http://testserver/admin/login/?next=%s" % url
        self.assertEqual(response.status_code, 302)
        self.assertEqual(expected_redirect_url, response.get("Location"))
