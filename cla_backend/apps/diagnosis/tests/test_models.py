from django.test import TestCase

from cla_common.constants import DIAGNOSIS_SCOPE

from core.tests.mommy_utils import make_recipe

from diagnosis.models import DiagnosisTraversal


class DiagnosisTraversalManagerTestCase(TestCase):
    def test_create_eligible(self):
        self.assertEqual(DiagnosisTraversal.objects.count(), 0)

        category = make_recipe('legalaid.category')
        diagnosis = DiagnosisTraversal.objects.create_eligible(
            category=category
        )

        self.assertEqual(DiagnosisTraversal.objects.count(), 1)

        self.assertEqual(diagnosis.category, category)
        self.assertEqual(diagnosis.state, DIAGNOSIS_SCOPE.INSCOPE)
