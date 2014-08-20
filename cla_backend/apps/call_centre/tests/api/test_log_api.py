from rest_framework.test import APITestCase

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin

from cla_eventlog.tests.test_views import LogAPIMixin


class LogViewSetTestCase(CLAOperatorAuthBaseApiTestMixin, LogAPIMixin, APITestCase):
    def get_http_authorization(self):
        return 'Bearer %s' % self.token
