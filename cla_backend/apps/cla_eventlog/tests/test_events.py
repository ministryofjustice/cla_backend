from datetime import timedelta

from cla_common.constants import REQUIRES_ACTION_BY
from django.test import TestCase
from django.utils.timezone import now

from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_ROLES, LOG_LEVELS
from cla_eventlog.events import BaseEvent
from cla_eventlog.models import Log
from cla_eventlog.tests.base import EventTestCaseMixin
from core.tests.mommy_utils import make_recipe, make_user
from legalaid.models import Case
from timer.models import Timer


class TestEvent(BaseEvent):
    key = "TEST_KEY"
    codes = {
        "TEST_CODE": {
            "type": LOG_TYPES.OUTCOME,
            "level": LOG_LEVELS.HIGH,
            "selectable_by": [],
            "description": "test code",
            "stops_timer": False,
        }
    }


class BaseEventTestCase(TestCase):
    def setUp(self):
        super(BaseEventTestCase, self).setUp()
        self.dummy_case = make_recipe("legalaid.case")
        self.dummy_user = make_user()

    def test_process_fails_with_wrong_code(self):
        event = TestEvent()
        self.assertRaises(
            KeyError, event.process, case=self.dummy_case, code="wrong-code", notes="", created_by=self.dummy_user
        )

    def test_process_with_given_code(self):
        """
        Test process by passing the code explicitly
        """

        class ThisTestEvent(TestEvent):
            codes = {
                "TEST_CODE1": {
                    "type": LOG_TYPES.OUTCOME,
                    "level": LOG_LEVELS.HIGH,
                    "selectable_by": [],
                    "description": "test code 1",
                    "stops_timer": False,
                },
                "TEST_CODE2": {
                    "type": LOG_TYPES.SYSTEM,
                    "level": LOG_LEVELS.MINOR,
                    "selectable_by": [],
                    "description": "test code 2",
                    "stops_timer": False,
                },
            }

        event = ThisTestEvent()

        self.assertEqual(Log.objects.count(), 0)

        event.process(case=self.dummy_case, code="TEST_CODE2", notes="test notes", created_by=self.dummy_user)

        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.first()
        self.assertEqual(log.code, "TEST_CODE2")
        self.assertEqual(log.notes, "test notes")
        self.assertEqual(log.level, LOG_LEVELS.MINOR)
        self.assertEqual(log.type, LOG_TYPES.SYSTEM)
        self.assertEqual(log.case, self.dummy_case)
        self.assertEqual(log.created_by, self.dummy_user)

    def test_process_with_implicit_code(self):
        """
        Test process without passing any codes. This should
        use the only one available in `codes`.
        """
        event = TestEvent()

        self.assertEqual(Log.objects.count(), 0)

        event.process(case=self.dummy_case, notes="test notes", created_by=self.dummy_user)

        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(Log.objects.first().code, "TEST_CODE")

    def test_process_with_implicit_code_fails_when_codes_gt_1(self):
        """
        Test process without passing any codes. This should fail
        when the Event defines `codes` with more than one items.
        """

        class ThisTestEvent(TestEvent):
            codes = {
                "TEST_CODE1": {
                    "type": LOG_TYPES.OUTCOME,
                    "level": LOG_LEVELS.HIGH,
                    "selectable_by": [],
                    "description": "test code 1",
                    "stops_timer": False,
                },
                "TEST_CODE2": {
                    "type": LOG_TYPES.SYSTEM,
                    "level": LOG_LEVELS.MINOR,
                    "selectable_by": [],
                    "description": "test code 2",
                    "stops_timer": False,
                },
            }

        event = ThisTestEvent()

        self.assertRaises(NotImplementedError, event.process, case=self.dummy_case, created_by=self.dummy_user)

    def test_process_with_running_timer(self):
        """
        If a timer is running, the Log created should have a fk to it
        """
        timer = make_recipe("timer.Timer", created_by=self.dummy_user)

        event = TestEvent()

        self.assertEqual(Log.objects.count(), 0)

        event.process(case=self.dummy_case, created_by=self.dummy_user)

        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(Log.objects.first().timer, timer)

    def test_process_without_running_timer(self):
        """
        If no timer is running, the Log created should have timer == None
        """
        event = TestEvent()

        self.assertEqual(Log.objects.count(), 0)

        event.process(case=self.dummy_case, created_by=self.dummy_user)

        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(Log.objects.first().timer, None)

    def test_process_stops_timer(self):
        """
        Process should stop the timer if the related code has
        `stops_timer` set to True
        """

        class ThisTestEvent(TestEvent):
            codes = {
                "TEST_CODE": {
                    "type": LOG_TYPES.OUTCOME,
                    "level": LOG_LEVELS.HIGH,
                    "selectable_by": [],
                    "description": "test code",
                    "stops_timer": True,
                }
            }

        timer = make_recipe("timer.Timer", created_by=self.dummy_user)

        event = ThisTestEvent()

        self.assertFalse(timer.stopped)
        self.assertEqual(Log.objects.count(), 0)

        event.process(case=self.dummy_case, created_by=self.dummy_user)

        self.assertEqual(Log.objects.count(), 1)

        timer = Timer.objects.get(pk=timer.pk)
        self.assertTrue(timer.stopped)

    def test_process_doesnt_update_requires_action_by(self):
        """
        If the code doesn't have `set_required_action_by` set,
        then `process` shouldn't update the value of `case.requires_action_by`
        """
        self.dummy_case.requires_action_by = REQUIRES_ACTION_BY.PROVIDER
        self.dummy_case.save()

        event = TestEvent()

        event.process(case=self.dummy_case, created_by=self.dummy_user)

        case = Case.objects.get(pk=self.dummy_case.pk)

        self.assertEqual(case.requires_action_by, REQUIRES_ACTION_BY.PROVIDER)

    def test_process_updates_requires_action_by(self):
        """
        If the code has `set_required_action_by` set, then `process`
        should update the value of case.requires_action_by
        """

        class ThisTestEvent(TestEvent):
            codes = {
                "TEST_CODE": {
                    "type": LOG_TYPES.OUTCOME,
                    "level": LOG_LEVELS.HIGH,
                    "selectable_by": [],
                    "description": "test code",
                    "stops_timer": False,
                    "set_requires_action_by": None,
                }
            }

        self.dummy_case.requires_action_by = REQUIRES_ACTION_BY.PROVIDER
        self.dummy_case.save()

        event = ThisTestEvent()

        event.process(case=self.dummy_case, created_by=self.dummy_user)

        case = Case.objects.get(pk=self.dummy_case.pk)

        self.assertEqual(case.requires_action_by, None)


class ConsecutiveOutcomeCodesTestCase(TestCase):
    def setUp(self):
        super(ConsecutiveOutcomeCodesTestCase, self).setUp()
        self.dummy_case = make_recipe("legalaid.case")
        self.dummy_user = make_user()
        self.log_attributes = dict(
            case=self.dummy_case, code="FOO", type=LOG_TYPES.OUTCOME, level=LOG_LEVELS.HIGH, created_by=self.dummy_user
        )

    def test_same_day_consecutive_outcome_code_not_allowed(self):
        l1 = Log(**self.log_attributes)
        l1.save()
        self.assertIsNotNone(l1.pk)
        l2 = Log(**self.log_attributes)
        l2.save()
        self.assertIsNone(l2.pk)

    def test_same_day_consecutive_outcome_code_with_matching_notes_not_allowed(self):
        l1 = Log(notes="foo", **self.log_attributes)
        l1.save()
        self.assertIsNotNone(l1.pk)
        l2 = Log(notes="foo", **self.log_attributes)
        l2.save()
        self.assertIsNone(l2.pk)

    def test_next_day_consecutive_outcome_code_allowed(self):
        yesterday = now() - timedelta(days=1)
        l1 = Log(**self.log_attributes)
        l1.save()
        self.assertIsNotNone(l1.pk)
        Log.objects.filter(pk=l1.pk).update(created=yesterday)
        l2 = Log(**self.log_attributes)
        l2.save()
        self.assertIsNotNone(l2.pk)

    def test_same_day_consecutive_outcome_code_allowed_with_notes(self):
        l1 = Log(**self.log_attributes)
        l1.save()
        self.assertIsNotNone(l1.pk)
        l2 = Log(notes="foo", **self.log_attributes)
        l2.save()
        self.assertIsNotNone(l2.pk)

    def test_same_day_non_consecutive_outcome_codes_allowed(self):
        for code in ["FOO", "BAR", "FOO"]:
            self.log_attributes["code"] = code
            log = Log(**self.log_attributes)
            log.save()
            self.assertIsNotNone(log.pk)


class SelectableEventsTestCase(EventTestCaseMixin, TestCase):
    def test_select_selectable_code(self):
        # get dict {event_key: [list of selectable codes]}
        selectable_events = event_registry.get_selectable_events(role=LOG_ROLES.OPERATOR)

        for chosen_key, chosen_codes in selectable_events.items():
            for chosen_code in chosen_codes:
                # chosen key / code

                event = event_registry.get_event(chosen_key)()
                res = event.process(
                    self.dummy_case, code=chosen_code, notes="selectable notes", created_by=self.dummy_user
                )

                self.assertLogEqual(
                    res,
                    Log(
                        case=self.dummy_case,
                        code=chosen_code,
                        type=LOG_TYPES.OUTCOME,
                        notes="selectable notes",
                        level=event.codes[chosen_code]["level"],
                        created_by=self.dummy_user,
                    ),
                )

    def test_select_selectable_code_invalid(self):
        # get dict {event_key: [list of selectable codes]}
        selectable_events = event_registry.get_selectable_events(role="admin")
        self.assertEqual(selectable_events, {})
