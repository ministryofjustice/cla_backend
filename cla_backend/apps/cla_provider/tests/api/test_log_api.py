from rest_framework.test import APITestCase
from rest_framework import status

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from core.tests.mommy_utils import make_recipe
from cla_common.constants import REQUIRES_ACTION_BY
from cla_eventlog.constants import LOG_LEVELS, LOG_TYPES


from cla_eventlog.tests.test_views import LogAPIMixin


class LogViewSetTestCase(CLAProviderAuthBaseApiTestMixin, LogAPIMixin, APITestCase):
    def make_parent_resource(self, **kwargs):
        kwargs.update({"provider": self.provider, "requires_action_by": REQUIRES_ACTION_BY.PROVIDER})
        return super(LogViewSetTestCase, self).make_parent_resource(**kwargs)

    def test_get_404_if_not_access_to_case(self):
        other_provider = make_recipe("cla_provider.provider")

        self.parent_resource.provider = other_provider
        self.parent_resource.save()

        response = self.client.get(self.list_url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_filtered_by_codes_parameter(self):
        """
        Test that when the 'codes' GET parameter is specified,
        LogViewSet.get_queryset() filters logs by the specified codes.
        """
        code_param = "CASE_VIEWED"

        make_recipe(
            "cla_eventlog.log",
            case=self.parent_resource,
            level=LOG_LEVELS.HIGH,
            type=LOG_TYPES.EVENT,
            code=code_param,
        )

        response = self.client.get(
            self.list_url,
            {"codes": code_param},
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_codes = [log["code"] for log in response.data]
        self.assertIn(code_param, response_codes)
        other_codes_in_response = set(response_codes) - {code_param}
        self.assertEqual(len(other_codes_in_response), 0)

    def test_get_filtered_by_multiple_codes_parameter(self):
        """
        Test that when multiple codes are specified in the 'codes' GET parameter
        as a list of value (eg. ?codes=CODE1&codes=CODE2), LogViewSet.get_queryset() filters logs by all specified codes.
        """
        codes_param = ("CASE_VIEWED", "REOPENED")
        make_recipe(
            "cla_eventlog.log",
            case=self.parent_resource,
            level=LOG_LEVELS.HIGH,
            type=LOG_TYPES.EVENT,
            code=codes_param[0],
        )

        make_recipe(
            "cla_eventlog.log",
            case=self.parent_resource,
            level=LOG_LEVELS.HIGH,
            type=LOG_TYPES.EVENT,
            code=codes_param[1],
        )

        response = self.client.get(
            self.list_url,
            {"codes": codes_param},
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_codes = [log["code"] for log in response.data]
        self.assertIn(codes_param[0], response_codes)
        self.assertIn(codes_param[1], response_codes)
        other_codes_in_response = set(response_codes) - set(codes_param)
        self.assertEqual(len(other_codes_in_response), 0)
