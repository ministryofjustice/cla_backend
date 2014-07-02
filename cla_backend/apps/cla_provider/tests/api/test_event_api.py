from rest_framework.test import APITestCase

from core.tests.test_base import CLAProviderAuthBaseApiTestMixin

from cla_eventlog.tests.test_views import EventAPIMixin


class EventViewSetTestCase(CLAProviderAuthBaseApiTestMixin, EventAPIMixin, APITestCase):
    pass
