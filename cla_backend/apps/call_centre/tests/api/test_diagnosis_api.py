from rest_framework.test import APITestCase

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin

from diagnosis.tests.diagnosis_api import DiagnosisAPIMixin


class DiagnosisTestCase(
    DiagnosisAPIMixin, CLAOperatorAuthBaseApiTestMixin, APITestCase
):
    API_URL_NAMESPACE = 'call_centre'

    def get_http_authorization(self):
        return 'Bearer %s' % self.token
