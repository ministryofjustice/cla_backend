from rest_framework.test import APITestCase

from core.tests.test_base import CLAProviderAuthBaseApiTestMixin

from cla_eventlog.tests.test_views import LogAPIMixin


class LogViewSetTestCase(
    CLAProviderAuthBaseApiTestMixin, LogAPIMixin, APITestCase
):
    pass
