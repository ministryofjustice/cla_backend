from cla_common.constants import REQUIRES_ACTION_BY
from core.tests.mommy_utils import make_recipe
from core.tests.test_base import NestedSimpleResourceAPIMixin
from rest_framework import status
from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin


class FeedbackAPIMixin(NestedSimpleResourceAPIMixin):
    LOOKUP_KEY = 'case_reference'
    RESOURCE_RECIPE = 'cla_provider.feedback'
    API_URL_BASE_NAME = 'feedback'
    PARENT_LOOKUP_KEY = 'reference'
    PARENT_RESOURCE_RECIPE = 'legalaid.case'
    PK_FIELD = 'case'
    ONE_TO_ONE_RESOURCE = False


    def make_resource(self, **kwargs):

        kwargs.update({
            'created_by': self.user.staff,
        })
        return super(FeedbackAPIMixin, self).make_resource(**kwargs)

    def make_parent_resource(self, **kwargs):
        kwargs.update({
            'provider': self.provider,
            'requires_action_by': REQUIRES_ACTION_BY.PROVIDER
        })
        return super(FeedbackAPIMixin, self).make_parent_resource(**kwargs)

    def test_methods_not_authorized(self):
        self._test_get_not_authorized(self.list_url, self.invalid_token)


class FeedbackAPITestCase(
    FeedbackAPIMixin, CLAProviderAuthBaseApiTestMixin, APITestCase
):
    def test_patch_comment_allowed(self):
        comment = "test"
        response = self.client.patch(
            self.detail_url,
            data={"comment": comment},
            format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], comment)

    def test_create_adds_current_user_as_created_by(self):
        created = self._create(data={'comment':'qqq'}, url=self.list_url)
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data['created_by'], self.user.username)

    def test_get_404_if_not_access_to_case(self):
        other_provider = make_recipe('cla_provider.provider')

        self.parent_resource.provider = other_provider
        self.parent_resource.save()

        response = self.client.get(
            self.list_url, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_other_fields_not_allowed(self):
        data = {
            'justified': not self.resource.justified,
            'resolved': not self.resource.resolved
        }
        resp = self.client.patch(
            self.detail_url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertEqual(resp.data['justified'], self.resource.justified)
        self.assertEqual(resp.data['resolved'], self.resource.resolved)
