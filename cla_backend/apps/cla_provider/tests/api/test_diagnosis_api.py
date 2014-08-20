from rest_framework.test import APITestCase

from cla_common.constants import REQUIRES_ACTION_BY

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from diagnosis.tests.diagnosis_api import DiagnosisAPIMixin


class DiagnosisTestCase(
    DiagnosisAPIMixin, CLAProviderAuthBaseApiTestMixin, APITestCase
):

    def setUp(self):
        super(DiagnosisTestCase, self).setUp()

        self.check_case.provider = self.provider
        self.check_case.requires_action_by = REQUIRES_ACTION_BY.PROVIDER
        self.check_case.save()
