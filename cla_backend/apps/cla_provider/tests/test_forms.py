from django.test import TestCase
from django.conf import settings

from model_mommy import mommy

from cla_common.constants import CASE_STATE_OPEN, CASE_STATE_ACCEPTED, \
    CASE_STATE_REJECTED, CASE_STATE_CLOSED

from legalaid.models import CaseOutcome, Case

from core.tests.test_base import make_recipe

from ..forms import CloseCaseForm, AcceptCaseForm, RejectCaseForm


class BaseStateFormTestCase(object):
    FORM = None,
    VALID_OUTCOME_CODE = None
    EXPECTED_CASE_STATE = None

    def setUp(self):
        super(BaseStateFormTestCase, self).setUp()

        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.outcome_codes = [
            make_recipe('legalaid.tests.outcome_code', code="CODE_OPEN", case_state=CASE_STATE_OPEN),
            make_recipe('legalaid.tests.outcome_code', code="CODE_ACCEPTED", case_state=CASE_STATE_ACCEPTED),
            make_recipe('legalaid.tests.outcome_code', code="CODE_REJECTED", case_state=CASE_STATE_REJECTED),
            make_recipe('legalaid.tests.outcome_code', code="CODE_CLOSED", case_state=CASE_STATE_CLOSED),
        ]

    def test_choices(self):
        form = self.FORM()

        self.assertItemsEqual(
            [f[1] for f in form.fields['outcome_code'].choices], [self.VALID_OUTCOME_CODE]
        )

    def test_save_successfull(self):
        case = make_recipe('legalaid.tests.case', state=CASE_STATE_OPEN)

        self.assertEqual(case.state, CASE_STATE_OPEN)

        self.assertEqual(CaseOutcome.objects.count(), 0)

        form = self.FORM(data={
            'outcome_code': self.VALID_OUTCOME_CODE,
            'outcome_notes': 'lorem ipsum'
        })

        self.assertTrue(form.is_valid())

        form.save(case, self.user)

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, self.EXPECTED_CASE_STATE)

        self.assertEqual(CaseOutcome.objects.count(), 1)
        outcome = CaseOutcome.objects.all()[0]

        self.assertEqual(outcome.outcome_code.code, self.VALID_OUTCOME_CODE)
        self.assertEqual(outcome.notes, 'lorem ipsum')

    def test_invalid_form(self):
        case = make_recipe('legalaid.tests.case', state=CASE_STATE_OPEN)

        self.assertEqual(case.state, CASE_STATE_OPEN)

        self.assertEqual(CaseOutcome.objects.count(), 0)

        form = self.FORM(data={
            'outcome_code': 'invalid',
            'outcome_notes': 'l'*501
        })

        self.assertFalse(form.is_valid())

        self.assertItemsEqual(
            form.errors, {
                'outcome_code': [u'Select a valid choice. That choice is not one of the available choices.'],
                'outcome_notes': [u'Ensure this value has at most 500 characters (it has 501).']
            }
        )

        # nothing has changed
        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATE_OPEN)

        self.assertEqual(CaseOutcome.objects.count(), 0)


class AcceptCaseFormTestCase(BaseStateFormTestCase, TestCase):
    FORM = AcceptCaseForm
    VALID_OUTCOME_CODE = 'CODE_ACCEPTED'
    EXPECTED_CASE_STATE = CASE_STATE_ACCEPTED


class RejectCaseFormTestCase(BaseStateFormTestCase, TestCase):
    FORM = RejectCaseForm
    VALID_OUTCOME_CODE = 'CODE_REJECTED'
    EXPECTED_CASE_STATE = CASE_STATE_REJECTED


class CloseCaseFormTestCase(BaseStateFormTestCase, TestCase):
    FORM = CloseCaseForm
    VALID_OUTCOME_CODE = 'CODE_CLOSED'
    EXPECTED_CASE_STATE = CASE_STATE_CLOSED
