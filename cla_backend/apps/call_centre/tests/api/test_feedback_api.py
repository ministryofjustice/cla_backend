from rest_framework.test import APITestCase

from core.tests.test_base import SimpleResourceAPIMixin
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin


class FeedbackAPITestCase(SimpleResourceAPIMixin, CLAOperatorAuthBaseApiTestMixin, APITestCase):
    RESOURCE_RECIPE = "cla_provider.feedback"
    LOOKUP_KEY = "reference"
    API_URL_BASE_NAME = "feedback"

    def setUp(self):
        super(FeedbackAPITestCase, self).setUp()
        self.operator.is_manager = True
        self.operator.save()

    @property
    def response_keys(self):
        return [
            "reference",
            "provider",
            "case",
            "created_by",
            "comment",
            "justified",
            "resolved",
            "created",
            "modified",
            "issue",
        ]

    def test_patch_comment_allowed(self):
        data = {"comment": self.resource.comment + u"test"}
        resp = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertResponseKeys(resp)
        self.assertEqual(resp.data["comment"], self.resource.comment)

    def test_patch_other_fields_allowed(self):
        data = {"justified": not self.resource.justified, "resolved": not self.resource.resolved}
        resp = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertResponseKeys(resp)
        self.assertEqual(resp.data["justified"], not self.resource.justified)
        self.assertEqual(resp.data["resolved"], not self.resource.resolved)

    def test_methods_not_allowed(self):
        self._test_delete_not_allowed(self.detail_url)
        self._test_post_not_allowed(self.detail_url)
        self._test_post_not_allowed(self.list_url)
        self._test_patch_not_allowed(self.list_url)

    def test_only_op_managers_can_access_endpoint(self):
        # checking that op manager can access endpoint first
        response = self.client.get(self.list_url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.detail_url, {}, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, 200)

        response = self.client.patch(self.detail_url, {}, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, 200)

        # then checking that normal op can't can't access endpoint
        self.operator.is_manager = False
        self.operator.save()

        response = self.client.get(self.list_url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, 403)

        response = self.client.get(self.detail_url, {}, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, 403)

        response = self.client.patch(self.detail_url, {}, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, 403)
