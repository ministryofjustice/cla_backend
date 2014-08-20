from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin

from cla_eventlog.tests.test_views import EventAPIMixin


class EventViewSetTestCase(CLAOperatorAuthBaseApiTestMixin, EventAPIMixin, APITestCase):
    pass
