from django.test import TestCase
from django.core.urlresolvers import reverse
from core.tests.mommy_utils import make_user


class KnowledgebaseArticleAdminViewTestCase(TestCase):
    def test_csv_import_access__unathenticated_user(self):
        url = reverse("admin:knowledgebase_import_csv")
        response = self.client.get(url)
        expected_redirect_url = "http://testserver/admin/login/?next=%s" % url
        self.assertEqual(response.status_code, 302)
        self.assertEqual(expected_redirect_url, response.get("Location"))

    def test_csv_import_access_authenticated_user(self):
        admin = make_user(is_staff=True, is_superuser=True, password="admin")
        admin.set_password("admin")
        admin.save()
        self.client.login(username=admin.username, password="admin")

        url = reverse("admin:knowledgebase_import_csv")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
