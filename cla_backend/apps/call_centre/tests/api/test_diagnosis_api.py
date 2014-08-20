from rest_framework.test import APITestCase

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin

from diagnosis.tests.diagnosis_api import DiagnosisAPIMixin


class DiagnosisTestCase(
    DiagnosisAPIMixin, CLAOperatorAuthBaseApiTestMixin, APITestCase
):
    pass
