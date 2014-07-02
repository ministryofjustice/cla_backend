from django.test import TestCase

from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_ROLES, LOG_LEVELS
from cla_eventlog.models import Log

from cla_eventlog.tests.base import EventTestCaseMixin


class RejectCaseEventTestCase(EventTestCaseMixin, TestCase):
    def test_reject_case(self):
        self._test_process_with_expicit_code(
            'reject_case', ['MIS', 'MIS-MEANS', 'MIS-OOS', 'COI']
        )

    def test_reject_conflict(self):
        self._test_process_with_implicit_code('reject_case', 'COI',
            process_kwargs={
                'is_conflict': True
            }
        )


class AcceptCaseEventTestCase(EventTestCaseMixin, TestCase):
    def test_accept_case(self):
        self._test_process_with_implicit_code('accept_case', 'SPOP')


class CloseCaseEventTestCase(EventTestCaseMixin, TestCase):
    def test_close_case(self):
        self._test_process_with_implicit_code('close_case', 'CLSP')
