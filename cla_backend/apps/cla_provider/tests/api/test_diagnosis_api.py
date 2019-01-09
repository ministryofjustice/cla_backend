from rest_framework.test import APITestCase

from cla_common.constants import REQUIRES_ACTION_BY

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from diagnosis.tests.diagnosis_api import DiagnosisAPIMixin


class DiagnosisTestCase(DiagnosisAPIMixin, CLAProviderAuthBaseApiTestMixin, APITestCase):
    def make_parent_resource(self, **kwargs):
        kwargs.update({"provider": self.provider, "requires_action_by": REQUIRES_ACTION_BY.PROVIDER})
        return super(DiagnosisTestCase, self).make_parent_resource(**kwargs)
