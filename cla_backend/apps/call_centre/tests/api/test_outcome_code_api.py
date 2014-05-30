from rest_framework.test import APITestCase

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin

from legalaid.tests.views.outcome_code_api import OutcomeCodeAPIMixin


class OutcomeCodeTests(CLAOperatorAuthBaseApiTestMixin, OutcomeCodeAPIMixin, APITestCase):
    pass
