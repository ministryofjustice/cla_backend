from rest_framework.test import APITestCase

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin

from timer.tests.test_views import TimerAPIMixin


class TimerViewSetTestCase(
    CLAOperatorAuthBaseApiTestMixin, TimerAPIMixin, APITestCase
):
    pass
