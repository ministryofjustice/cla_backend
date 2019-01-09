import mock
import datetime

from django.test import TestCase
from django.utils import timezone

from core.tests.mommy_utils import make_recipe, make_user

from legalaid.models import Case

from timer.models import Timer


class TimerTestCase(TestCase):
    def test_start(self):
        self.assertEqual(Timer.objects.count(), 0)
        user = make_user()

        timer = Timer.start(user)

        self.assertEqual(Timer.objects.count(), 1)
        self.assertEqual(Timer.objects.first(), timer)

    def test_stop_fails_if_already_stopped(self):
        timer = make_recipe("timer.Timer", stopped=timezone.now())

        self.assertRaises(ValueError, timer.stop)

    def test_stop_fails_if_no_log_exists(self):
        timer = make_recipe("timer.Timer", stopped=None)

        self.assertRaises(ValueError, timer.stop)

    def test_stop_success(self):
        timer = make_recipe("timer.Timer", stopped=None)
        case = make_recipe("legalaid.Case")
        make_recipe("cla_eventlog.Log", timer=timer, case=case)

        self.assertEqual(timer.stopped, None)
        self.assertEqual(timer.linked_case, None)

        timer.stop()

        timer = Timer.objects.get(pk=timer.pk)  # reloading

        self.assertNotEqual(timer.stopped, None)
        self.assertEqual(timer.linked_case, case)

    @mock.patch("timer.models.postgres_now")
    def test_billable_time_with_2_stopped_timers(self, mocked_now):
        """
            DB:
                timer1: on case A, by user A, stopped
                timer2: on case A, by user A, stopped by this test
                timer3: on case A, by user B, stopped
                timer4: on case A, by user B, running (should be ignored)
                timer5: on case B, by user A, stopped (should be ignored)
                timer6: on no case, by user A, cancelled (should be ignored)

            Expected:
                case A.billable_time == timer1 + timer2 + timer3
        """

        def build_datetime(date_str):
            dt = datetime.datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")

            return dt.replace(tzinfo=timezone.get_current_timezone())

        # DATABASE SETUP

        caseA = make_recipe("legalaid.Case")
        caseB = make_recipe("legalaid.Case")

        userA = make_user()
        userB = make_user()

        timer1 = make_recipe(
            "timer.Timer",
            created=build_datetime("01/01/2014 10:00:00"),
            stopped=build_datetime("01/01/2014 10:00:01"),
            linked_case=caseA,
            created_by=userA,
        )
        timer2 = make_recipe(
            "timer.Timer",
            created=build_datetime("01/04/2014 11:00:00"),
            stopped=None,
            linked_case=caseA,
            created_by=userA,
        )
        timer3 = make_recipe(
            "timer.Timer",
            created=build_datetime("01/02/2014 23:00:00"),
            stopped=build_datetime("02/02/2014 01:00:01"),
            linked_case=caseA,
            created_by=userB,
        )
        timer4 = make_recipe("timer.Timer", stopped=None, linked_case=caseA, created_by=userB)
        timer5 = make_recipe(
            "timer.Timer", stopped=build_datetime("02/02/2014 01:00:01"), linked_case=caseB, created_by=userA
        )
        timer6 = make_recipe(
            "timer.Timer",
            stopped=build_datetime("02/02/2014 01:00:01"),
            linked_case=caseB,
            created_by=userA,
            cancelled=True,
        )

        make_recipe("cla_eventlog.Log", timer=timer2, case=caseA)
        make_recipe("cla_eventlog.Log", timer=timer4, case=caseA)

        # CHECKS BEFORE STOPPING THE TIMER

        self.assertEqual(caseA.billable_time, 0)
        self.assertEqual(caseB.billable_time, 0)

        mocked_now.return_value = build_datetime("01/04/2014 11:05:00")
        timer2.stop()

        # reloading objects
        caseA = Case.objects.get(pk=caseA.pk)
        caseB = Case.objects.get(pk=caseB.pk)

        # CHECKING CALCULATED BILLABLE TIME

        self.assertEqual(caseA.billable_time, 7502)
        self.assertEqual(caseB.billable_time, 0)

    def test_billable_time(self):
        case = make_recipe("legalaid.Case")
        user = make_user()

        timer = make_recipe("timer.Timer", linked_case=case, created_by=user)

        make_recipe("cla_eventlog.Log", timer=timer, case=case)

        timer.stop()

        self.assertEqual(case.billable_time, 0)
