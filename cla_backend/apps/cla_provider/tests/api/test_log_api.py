from rest_framework.test import APITestCase
from rest_framework import status

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from core.tests.mommy_utils import make_recipe
from cla_common.constants import REQUIRES_ACTION_BY

from cla_eventlog.tests.test_views import LogAPIMixin


class LogViewSetTestCase(
    CLAProviderAuthBaseApiTestMixin, LogAPIMixin, APITestCase
):
    def make_parent_resource(self, **kwargs):
        kwargs.update({
            'provider': self.provider,
            'requires_action_by': REQUIRES_ACTION_BY.PROVIDER
        })
        return super(LogViewSetTestCase, self).make_parent_resource(
            **kwargs
        )

    def test_get_404_if_not_access_to_case(self):
        other_provider = make_recipe('cla_provider.provider')

        self.parent_resource.provider = other_provider
        self.parent_resource.save()

        response = self.client.get(
            self.list_url, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
