from django.test import TestCase

from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_ROLES, LOG_LEVELS
from cla_eventlog.models import Log

from cla_eventlog.tests.base import EventTestCaseMixin


class RejectCaseEventTestCase(EventTestCaseMixin, TestCase):
    def test_reject_case(self):
        event = event_registry.get_event('reject_case')()
        codes = event.get_selectable_codes(role=LOG_ROLES.SPECIALIST)

        self.assertItemsEqual(codes, ['MIS', 'MIS-MEANS', 'MIS-OOS'])

        chosen_code = codes[0]
        res = event.process(
            self.dummy_case, code=chosen_code, notes='this is a note',
            created_by=self.dummy_user
        )

        self.assertLogEqual(res, Log(
            case=self.dummy_case, code=chosen_code,
            type=LOG_TYPES.OUTCOME, notes='this is a note',
            level=LOG_LEVELS.HIGH, created_by=self.dummy_user)
        )


class AcceptCaseEventTestCase(EventTestCaseMixin, TestCase):
    def test_accept_case(self):
        self._test_process_event_key_with_one_code('accept_case', 'SPOP')


class CloseCaseEventTestCase(EventTestCaseMixin, TestCase):
    def test_close_case(self):
        self._test_process_event_key_with_one_code('close_case', 'CLSP')
