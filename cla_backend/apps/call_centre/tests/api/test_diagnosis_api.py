from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin

from diagnosis.tests.diagnosis_api import DiagnosisAPIMixin


class DiagnosisTestCase(
    DiagnosisAPIMixin, CLAOperatorAuthBaseApiTestMixin, APITestCase
):
    pass
