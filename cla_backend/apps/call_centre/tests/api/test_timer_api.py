from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from timer.tests.test_views import TimerAPIMixin


class TimerViewSetTestCase(
    CLAOperatorAuthBaseApiTestMixin, TimerAPIMixin, APITestCase
):
    pass
