from core.tests.mommy_utils import make_recipe

from django.test import TestCase

from cla_eventlog import event_registry

from cla_eventlog.tests.base import EventTestCaseMixin
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS


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


class CallMeBackEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'call_me_back'

    def test_CB1(self):
        self._test_process_with_implicit_code('CB1')

    def test_CB2(self):
        case = make_recipe('legalaid.case', callback_attempt=1)
        self._test_process_with_implicit_code('CB2', dummy_case=case)

    def test_CB3(self):
        case = make_recipe('legalaid.case', callback_attempt=2)
        self._test_process_with_implicit_code('CB3', dummy_case=case)

    def test_CB4_errors(self):
        dummy_case = make_recipe('legalaid.case', callback_attempt=3)

        event = event_registry.get_event(self.EVENT_KEY)()

        self.assertRaises(ValueError, event.process, **{
            'case': dummy_case,
            'notes': 'this is a note',
            'created_by': self.dummy_user
        })

        self.assertEqual(dummy_case.log_set.count(), 0)


class StopCallMeBackEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'stop_call_me_back'

    def test_CBC(self):
        # with callback_attempt == 1
        case = make_recipe('legalaid.case', callback_attempt=1)
        self._test_process_with_implicit_code('CBC', dummy_case=case, process_kwargs={
            'cancel': True
        })

        # with callback_attempt == 2
        case = make_recipe('legalaid.case', callback_attempt=2)
        self._test_process_with_implicit_code('CBC', dummy_case=case, process_kwargs={
            'cancel': True
        })

        # with callback_attempt == 3
        case = make_recipe('legalaid.case', callback_attempt=3)
        self._test_process_with_implicit_code('CBC', dummy_case=case, process_kwargs={
            'cancel': True
        })

    def test_CBC_errors_without_prev_CBx(self):
        dummy_case = make_recipe('legalaid.case', callback_attempt=0)

        event = event_registry.get_event(self.EVENT_KEY)()

        self.assertRaises(ValueError, event.process, **{
            'case': dummy_case,
            'notes': 'this is a note',
            'created_by': self.dummy_user,
            'cancel': True
        })

        self.assertEqual(dummy_case.log_set.count(), 0)

    def test_CALLBACK_COMPLETE(self):
        # with callback_attempt == 1
        case = make_recipe('legalaid.case', callback_attempt=1)
        self._test_process_with_implicit_code('CALLBACK_COMPLETE', dummy_case=case,
            expected_type=LOG_TYPES.SYSTEM, expected_level=LOG_LEVELS.MINOR,
            process_kwargs={
                'complete': True
            }
        )

        # with callback_attempt == 2
        case = make_recipe('legalaid.case', callback_attempt=2)
        self._test_process_with_implicit_code('CALLBACK_COMPLETE', dummy_case=case,
            expected_type=LOG_TYPES.SYSTEM, expected_level=LOG_LEVELS.MINOR,
            process_kwargs={
                'complete': True
            }
        )

        # with callback_attempt == 3
        case = make_recipe('legalaid.case', callback_attempt=3)
        self._test_process_with_implicit_code('CALLBACK_COMPLETE', dummy_case=case,
            expected_type=LOG_TYPES.SYSTEM, expected_level=LOG_LEVELS.MINOR,
            process_kwargs={
                'complete': True
            },
        )

    def test_CALLBACK_COMPLETE_errors_without_prev_CBx(self):
        dummy_case = make_recipe('legalaid.case', callback_attempt=0)

        event = event_registry.get_event(self.EVENT_KEY)()

        self.assertRaises(ValueError, event.process, **{
            'case': dummy_case,
            'notes': 'this is a note',
            'created_by': self.dummy_user,
            'complete': True
        })

        self.assertEqual(dummy_case.log_set.count(), 0)
