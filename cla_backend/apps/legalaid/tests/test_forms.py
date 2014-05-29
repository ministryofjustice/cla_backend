from django.test import TestCase
from legalaid.models import CaseLog

from core.tests.mommy_utils import make_recipe, make_user

from ..forms import OutcomeForm


class OutcomeFormTestCase(TestCase):
    def test_save(self):
        outcome_codes = make_recipe('legalaid.logtype', _quantity=2, subtype='outcome')
        case = make_recipe('legalaid.case')
        user = make_user()

        form = OutcomeForm(case=case, data={
            'outcome_code': outcome_codes[0].code,
            'outcome_notes': 'lorem ipsum',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(CaseLog.objects.count(), 0)

        form.save(user)

        self.assertEqual(CaseLog.objects.count(), 1)
        self.assertEqual(CaseLog.objects.all()[0].case, case)
