from cla_common.constants import REQUIRES_ACTION_BY
from cla_provider.tests.api.test_feedback_api import FeedbackAPIMixin
from core.tests.mommy_utils import make_recipe
from core.tests.test_base import NestedSimpleResourceAPIMixin, \
    SimpleResourceAPIMixin
from rest_framework import status
from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin




class FeedbackAPITestCase(
    SimpleResourceAPIMixin, CLAOperatorAuthBaseApiTestMixin, APITestCase
):
    RESOURCE_RECIPE = 'cla_provider.feedback'
    LOOKUP_KEY = 'reference'
    API_URL_BASE_NAME = 'feedback'

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
            "modified"
        ]

    def test_patch_comment_allowed(self):
        data = {
            'comment': self.resource.comment+u'test'
        }
        resp = self.client.patch(
            self.detail_url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertResponseKeys(resp)
        self.assertEqual(resp.data['comment'], self.resource.comment)

    def test_patch_other_fields_allowed(self):
        data = {
            'justified': not self.resource.justified,
            'resolved': not self.resource.resolved
        }
        resp = self.client.patch(
            self.detail_url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertResponseKeys(resp)
        self.assertEqual(resp.data['justified'], not self.resource.justified)
        self.assertEqual(resp.data['resolved'], not self.resource.resolved)

    def test_methods_not_allowed(self):
        self._test_delete_not_allowed(self.detail_url)
        self._test_post_not_allowed(self.detail_url)
        self._test_post_not_allowed(self.list_url)
        self._test_patch_not_allowed(self.list_url)
