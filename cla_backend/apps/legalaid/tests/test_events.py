from django.test import TestCase

from core.tests.mommy_utils import make_recipe

from cla_eventlog import event_registry
from cla_eventlog.models import Log
from cla_eventlog.tests.base import EventTestCaseMixin
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS


class CaseEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'case'

    def test_case_created(self):
        self._test_process_with_implicit_code(
            'CASE_CREATED',
            process_kwargs={
                'status': 'created'
            },
            expected_type=LOG_TYPES.SYSTEM
        )

    def test_case_viewed(self):
        self._test_process_with_implicit_code(
            'CASE_VIEWED',
            process_kwargs={
                'status': 'viewed'
            },
            expected_type=LOG_TYPES.SYSTEM,
            expected_level=LOG_LEVELS.MINOR
        )


class CaseEventAvoidDuplicatesTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'case'

    def test_CASE_VIEWED_log_not_created_after_CASE_CREATED_during_timer(self):
        """
        During the lifetime of a timer, if a user creates a case
        and then views it, only 'CASE_CREATED' log is created.

        In other words, we don't log 'CASE_VIEWED' to avoid noise.
        """
        event = event_registry.get_event(self.EVENT_KEY)()

        self.assertEqual(Log.objects.count(), 0)  # no logs

        # db setup
        make_recipe('timer.Timer', created_by=self.dummy_user)

        # case created
        event.process(**{
            'case': self.dummy_case,
            'created_by': self.dummy_user,
            'status': 'created'
        })

        self.assertEqual(Log.objects.count(), 1)

        # case viewed log not created because case created log
        # already exists
        event.process(**{
            'case': self.dummy_case,
            'created_by': self.dummy_user,
            'status': 'viewed'
        })

        self.assertEqual(Log.objects.count(), 1)

    def test_CASE_VIEWED_log_not_created_after_CASE_VIEWED_during_timer(self):
        """
        During the lifetime of a timer, if a user viewed a case twice, we
        should only log CASE_VIEWED once.
        """
        event = event_registry.get_event(self.EVENT_KEY)()

        self.assertEqual(Log.objects.count(), 0)  # no logs

        # db setup
        make_recipe('timer.Timer', created_by=self.dummy_user)

        # case viewed
        event.process(**{
            'case': self.dummy_case,
            'created_by': self.dummy_user,
            'status': 'viewed'
        })

        self.assertEqual(Log.objects.count(), 1)

        # case viewed log not created because case created log
        # already exists
        event.process(**{
            'case': self.dummy_case,
            'created_by': self.dummy_user,
            'status': 'viewed'
        })

        self.assertEqual(Log.objects.count(), 1)

    def test_CASE_VIEWED_log_created_after_CASE_CREATED_if_no_timer(self):
        """
        If no timer exists, CASE_VIEWED logs are always created, even after
        CASE_CREATED logs.
        """

        event = event_registry.get_event(self.EVENT_KEY)()

        # case created
        event.process(**{
            'case': self.dummy_case,
            'created_by': self.dummy_user,
            'status': 'created'
        })

        self.assertEqual(Log.objects.count(), 1)

        # case viewed
        event.process(**{
            'case': self.dummy_case,
            'created_by': self.dummy_user,
            'status': 'viewed'
        })

        self.assertEqual(Log.objects.count(), 2)

    def test_CASE_VIEWED_log_created_after_CASE_VIEWED_if_no_timer(self):
        event = event_registry.get_event(self.EVENT_KEY)()

        # case viewed 1
        event.process(**{
            'case': self.dummy_case,
            'created_by': self.dummy_user,
            'status': 'viewed'
        })

        self.assertEqual(Log.objects.count(), 1)

        # case viewed 2
        event.process(**{
            'case': self.dummy_case,
            'created_by': self.dummy_user,
            'status': 'viewed'
        })

        self.assertEqual(Log.objects.count(), 2)


class SuspendCaseEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'suspend_case'

    CODES = ['INSUF', 'ABND', 'TERM', 'IRCB', 'COPE', 'DUPL', 'RDSP', 'SAME', 'WROF', 'MRNB', 'MRCC']

    def test_INSUF(self):
        self._test_process_with_expicit_code_and_requires_action_None_if_op_or_op_manager(
            self.CODES, code='INSUF', expected_level=LOG_LEVELS.HIGH
        )

    def test_ABND(self):
        self._test_process_with_expicit_code_and_requires_action_None_if_op_or_op_manager(
            self.CODES, code='ABND', expected_level=LOG_LEVELS.HIGH
        )

    def test_TERM(self):
        self._test_process_with_expicit_code_and_requires_action_None_if_op_or_op_manager(
            self.CODES, code='TERM', expected_level=LOG_LEVELS.HIGH
        )

    def test_IRCB(self):
        self._test_process_with_expicit_code(self.CODES, code='IRCB')

    def test_COPE(self):
        self._test_process_with_expicit_code_and_requires_action_None_if_op_or_op_manager(
            self.CODES, code='COPE', expected_level=LOG_LEVELS.HIGH
        )

    def test_DUPL(self):
        self._test_process_with_expicit_code_and_requires_action_None_if_op_or_op_manager(
            self.CODES, code='DUPL', expected_level=LOG_LEVELS.HIGH
        )

    def test_RDSP(self):
        self._test_process_with_expicit_code_and_requires_action_None_if_op_or_op_manager(
            self.CODES, code='RDSP', expected_level=LOG_LEVELS.HIGH
        )

    def test_WROF(self):
        self._test_process_with_expicit_code_and_requires_action_None_if_op_or_op_manager(
            self.CODES, code='WROF', expected_level=LOG_LEVELS.HIGH
        )

    def test_SAME(self):
        self._test_process_with_expicit_code_and_requires_action_None_if_op_or_op_manager(
            self.CODES, code='SAME', expected_level=LOG_LEVELS.HIGH
        )
