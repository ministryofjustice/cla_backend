from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from cla_eventlog.tests.test_views import LogAPIMixin


class LogViewSetTestCase(
    CLAProviderAuthBaseApiTestMixin, LogAPIMixin, APITestCase
):
    pass
