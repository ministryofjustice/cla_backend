import mock

from core.tests.mommy_utils import make_recipe

from django.test import TestCase

from cla_common.constants import REQUIRES_ACTION_BY, ELIGIBILITY_STATES

from legalaid.models import Case

from cla_eventlog.tests.base import EventTestCaseMixin


class AssignToProviderEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'assign_to_provider'

    def test_assign_to_provider_manually(self):
        eligible_case = make_recipe('legalaid.eligible_case')
        self._test_process_with_implicit_code(
            'MANALC',
            process_kwargs={
                'is_manual': True
            },
            dummy_case=eligible_case
        )

    def test_assign_to_provider_automatically(self):
        eligible_case = make_recipe('legalaid.eligible_case')
        self.assertEqual(eligible_case.eligibility_check.state, 'yes')
        self._test_process_with_implicit_code(
            'REFSP',
            process_kwargs={
                'is_manual': False
            },
            dummy_case=eligible_case
        )

    def test_assign_to_provider_automatically_ineligible_case(self):
        eligible_case = make_recipe('legalaid.case')
        self.assertNotEqual(eligible_case.eligibility_check.state, 'yes')
        self._test_process_with_implicit_code(
            'SPOR',
            process_kwargs={
                'is_manual': False,
                'is_spor': True
            }
        )

    def test_assign_to_provider_manually_ineligible_case(self):
        eligible_case = make_recipe('legalaid.case')
        self.assertNotEqual(eligible_case.eligibility_check.state, 'yes')
        self._test_process_with_implicit_code(
            'SPOR',
            process_kwargs={
                'is_manual': True,
                'is_spor': True
            }
        )


class DeferAssignmentEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'defer_assignment'

    def test_defer_assignment(self):
        self._test_process_with_implicit_code('CBSP')


class DeclineHelpEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'decline_help'
    CODES = ['DESP', 'DECL', 'NRES']

    def test_DESP(self):
        self._test_process_with_expicit_code_and_requires_action_None_if_operator(
            self.CODES, code='DESP'
        )

    def test_DECL(self):
        self._test_process_with_expicit_code_and_requires_action_None_if_operator(
            self.CODES, code='DECL'
        )

    def test_NRES(self):
        self._test_process_with_expicit_code_and_requires_action_None_if_operator(
            self.CODES, code='NRES'
        )
