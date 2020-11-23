# coding=utf-8
from contextlib import contextmanager
import datetime

from django.test import TestCase
from django.utils import timezone
import mock

from cla_common.constants import CASE_SOURCE
from cla_common import call_centre_availability
from core.tests.mommy_utils import make_recipe, make_user
from cla_eventlog import event_registry
from cla_eventlog.models import Log
from legalaid.forms import get_sla_time
from reports.forms import MICB1Extract
from call_centre.tests.test_utils import CallCentreFixedOperatingHours


def _make_datetime(year=None, month=None, day=None, hour=0, minute=0, second=0):
    today = datetime.date.today()
    year = year if year else today.year
    month = month if month else today.month
    day = day if day else today.day
    dt = datetime.datetime(year, month, day, hour, minute, second)
    return timezone.make_aware(dt, timezone.get_current_timezone())


def mock_now(dt):
    return dt


@contextmanager
def patch_field(cls, field_name, dt):
    field = cls._meta.get_field(field_name)
    with mock.patch.object(field, "default", new=mock_now(dt)):
        yield


class MiSlaTestCaseBase(CallCentreFixedOperatingHours):
    source = None
    requires_action_at_minutes_offset = 60

    def setUp(self):
        super(MiSlaTestCaseBase, self).setUp()
        self.current_case = None
        self.now = self.get_default_dt()

        self.timezone_mock = mock.patch.object(timezone, "now", lambda: self.now)
        self.timezone_mock.start()

        now_naive = timezone.make_naive(self.now, timezone.get_current_timezone())
        self.cla_common_datetime_mock = mock.patch.object(
            call_centre_availability, "current_datetime", lambda: now_naive
        )
        self.cla_common_datetime_mock.start()

    def tearDown(self):
        super(MiSlaTestCaseBase, self).tearDown()
        self.timezone_mock.stop()
        self.cla_common_datetime_mock.stop()

    def get_default_dt(self):
        raise NotImplementedError()

    def get_requires_action_at(self):
        raise NotImplementedError

    def get_sla1_datetime(self):
        raise NotImplementedError()

    def get_sla2_datetime(self):
        raise NotImplementedError()

    def move_time_forward_minutes_before_sla1(self, minutes):
        return self._move_time_forward(self.get_sla1_datetime(), -minutes)

    def move_time_forward_minutes_after_sla1(self, minutes):
        return self._move_time_forward(self.get_sla1_datetime(), minutes)

    def move_time_forward_minutes_before_sla2(self, minutes):
        return self._move_time_forward(self.get_sla2_datetime(), -minutes)

    def move_time_forward_minutes_after_sla2(self, minutes):
        return self._move_time_forward(self.get_sla2_datetime(), minutes)

    def _move_time_forward(self, dt, minutes_forward):
        self.now = dt + datetime.timedelta(minutes=minutes_forward)
        self.timezone_mock.return_value = self.now
        self.cla_common_datetime_mock.return_value = timezone.make_naive(dt, dt.tzinfo)

        return self.now

    def make_case(self, dt, **kwargs):
        with patch_field(Log, "created", dt - datetime.timedelta(minutes=1)):
            self.current_case = make_recipe("legalaid.case", source=self.source, **kwargs)
            return self.current_case

    def schedule_callback(self, case, user, created, requires_action_at=None):
        requires_action_at = requires_action_at or created + datetime.timedelta(minutes=35)
        sla_base_time = requires_action_at
        if case.source in [CASE_SOURCE.SMS, CASE_SOURCE.VOICEMAIL]:
            sla_base_time = case.created
        event = event_registry.get_event("call_me_back")()
        with patch_field(Log, "created", created):
            event.get_log_code(case=case)
            event.process(
                case,
                created_by=user,
                notes="",
                context={
                    "requires_action_at": requires_action_at,
                    "sla_15": get_sla_time(sla_base_time, 15),
                    "sla_30": get_sla_time(sla_base_time, 30),
                    "sla_120": get_sla_time(sla_base_time, 120),
                    "sla_480": get_sla_time(sla_base_time, 480),
                    "sla_72h": get_sla_time(sla_base_time, 4320),
                },
            )
            case.set_requires_action_at(requires_action_at)

    def start_call(self, case, user, created):
        event = event_registry.get_event("case")()
        with patch_field(Log, "created", created):
            event.process(case, status="call_started", created_by=user, notes="Call started")

    def get_report(self, date_range):
        with mock.patch("reports.forms.MICB1Extract.date_range", date_range):
            report = MICB1Extract()

            qs = report.get_queryset()
            headers = report.get_headers()

        return {k: v for k, v in zip(headers, qs[0])}

    def create_and_get_report(self, callback_minutes_after, case=None):
        created = case.created if case else _make_datetime(2015, 1, 2, 9, 1, 0)
        case = case or self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        requires_action_at = created + datetime.timedelta(minutes=self.requires_action_at_minutes_offset)
        self.schedule_callback(case, user, created, requires_action_at)
        self.start_call(case, user, requires_action_at + datetime.timedelta(minutes=callback_minutes_after))

        date_range = (
            created.replace(hour=0, minute=0),
            created.replace(hour=0, minute=0) + datetime.timedelta(days=1),
        )
        return self.get_report(date_range)

    def test_current_time_within_sla1(self):
        case = self.make_case(self.now, created=self.now)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create a callback that is due now 1 hour from now
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())

        # Move current time to 1 minute before SLA1
        now_tz = self.move_time_forward_minutes_before_sla1(minutes=1)

        # Generate report without a callback
        date_range = (now_tz - datetime.timedelta(days=2), now_tz + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

        # Start a call
        self.start_call(case, user, now_tz)
        # Generate report with a successful callback
        date_range = (now_tz - datetime.timedelta(days=2), now_tz + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_current_time_after_sla1(self):
        case = self.make_case(self.now, created=self.now)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create a callback that is due now 1 hour from now
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())

        # Move current time to 1 minute after SLA1
        now_tz = self.move_time_forward_minutes_after_sla1(minutes=1)

        # Generate report without a callback
        date_range = (now_tz - datetime.timedelta(days=2), now_tz + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

        # Start a call
        self.start_call(case, user, now_tz)
        # Generate report with a successful callback
        date_range = (now_tz - datetime.timedelta(days=2), now_tz + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_current_time_before_sla2(self):
        case = self.make_case(self.now, created=self.now)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create a callback that is due now 1 hour from now
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())

        # Move current time to 1 minute before SLA2
        self.move_time_forward_minutes_before_sla2(minutes=1)

        # Generate report without a callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

        # Start a call
        self.start_call(case, user, self.now)
        # Generate report with a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_current_time_after_sla2(self):
        case = self.make_case(self.now, created=self.now)
        user = make_user()
        make_recipe("call_centre.operator", user=user)
        # Create a callback that is due now
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())

        # Move current time to 1 minute after SLA2
        now_tz = self.move_time_forward_minutes_after_sla2(minutes=1)

        # Generate report without a callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertTrue(values["missed_sla_2"])

        # Start a call
        self.start_call(case, user, now_tz)
        # Generate report with a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertTrue(values["missed_sla_2"])

    def test_cb2_current_time_within_sla1(self):
        case = self.make_case(self.now, created=self.now)
        user = make_user()
        make_recipe("call_centre.operator", user=user)
        # Create CB1
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())
        # Move current time to 1 minute before SLA1
        self.move_time_forward_minutes_before_sla1(minutes=1)
        # Create  CB2
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())

        # Generate report without a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

        # Start a call
        self.start_call(case, user, self.now)
        # Generate report with a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb2_current_time_after_sla1(self):
        case = self.make_case(self.now, created=self.now)
        user = make_user()
        make_recipe("call_centre.operator", user=user)
        # Create CB1
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())
        # Move current time 1 minute after SLA1
        now_tz = self.move_time_forward_minutes_after_sla1(minutes=1)
        # Create  CB2
        self.schedule_callback(case, user, created=now_tz, requires_action_at=self.get_requires_action_at())

        # Generate report without a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

        # Start a call
        self.start_call(case, user, now_tz)
        # Generate report with a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb2_current_time_before_sla2(self):
        case = self.make_case(self.now, created=self.now)
        user = make_user()
        make_recipe("call_centre.operator", user=user)
        # Create CB1
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())
        # Move current time 1 minute before SLA2
        self.move_time_forward_minutes_before_sla2(minutes=1)
        # Create  CB2
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())

        # Generate report without a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

        # Start a call
        self.start_call(case, user, self.now)
        # Generate report with a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb2_current_time_after_sla2(self):
        case = self.make_case(self.now, created=self.now)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB1
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())
        # Move current time 1 minute after SLA2
        self.move_time_forward_minutes_after_sla2(minutes=1)
        # Create  CB2
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())

        # Generate report without a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertTrue(values["missed_sla_2"])

        # Start a call
        self.start_call(case, user, self.now)
        # Generate report with a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertTrue(values["missed_sla_2"])

    def test_cb3_current_time_within_sla1(self):
        case = self.make_case(self.now, created=self.now)
        user = make_user()
        make_recipe("call_centre.operator", user=user)
        # Create CB1
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())

        # Move current time to 2 minute before SLA1
        self.move_time_forward_minutes_before_sla1(minutes=2)
        # Create  CB2
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())

        # Move current time to 1 minute before SLA1
        self.move_time_forward_minutes_before_sla1(minutes=1)
        # Create  CB3
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())

        # Generate report without a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

        # Start a call
        self.start_call(case, user, self.now)
        # Generate report with a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])


class MiSlaTestCaseWeb(MiSlaTestCaseBase, TestCase):
    source = CASE_SOURCE.WEB

    # fmt: off
    """
    CB1
    +--------------+-------------------------------+---------------------------------------------+--------------------------------+
    |              |                               |                                             | Call answered                  |
    |              |                               |                                             | after 30m                      |
    |              | Call answered                 | Call answered                               | AND                            |
    |              | Within 30m window             | before 30m window                           | current time within 72h window |
    +--------------+-------------------------------+---------------------------------------------+--------------------------------+
    | SLA 1 missed |             FALSE             |                     TRUE                    |              TRUE              |
    +--------------+-------------------------------+---------------------------------------------+--------------------------------+
    | SLA 2 missed |             FALSE             |                    FALSE                    |              FALSE             |
    +--------------+-------------------------------+---------------------------------------------+--------------------------------+
    | test         | test_current_time_within_sla1 | test_current_time_before_requires_action_at | test_current_time_after_sla1   |
    +--------------+-------------------------------+---------------------------------------------+--------------------------------+

    CB2
    +--------------+-----------------------------------+-------------------------------------------------+----------------------------------+----------------------------------+----------------------------------+-----------------------------------+
    |              | CB2 Scheduled                     | CB2 Scheduled                                   | CB2 Scheduled                    | CB2 Scheduled                    | Call answered                    | CB2 Scheduled                     |
    |              | within 30m window                 | before 30m window                               | after 30m window                 | after 30m window                 | after 72 window                  | within 30m window                 |
    |              | AND                               | AND                                             | AND                              | AND                              |                                  | AND                               |
    |              | current time within 72h window    | current time within 72h window                  | current time within 72h window   | current time after 72h window    |                                  | call answered within 72 window    |
    +--------------+-----------------------------------+-------------------------------------------------+----------------------------------+----------------------------------+----------------------------------+-----------------------------------+
    | SLA 1 missed |               FALSE               |                       TRUE                      |               TRUE               |               TRUE               |               TRUE               |               FALSE               |
    +--------------+-----------------------------------+-------------------------------------------------+----------------------------------+----------------------------------+----------------------------------+-----------------------------------+
    | SLA 2 missed |               FALSE               |                      FALSE                      |               FALSE              |               TRUE               |               TRUE               |               FALSE               |
    +--------------+-----------------------------------+-------------------------------------------------+----------------------------------+----------------------------------+----------------------------------+-----------------------------------+
    | test         | test_cb2_current_time_within_sla1 | test_cb2_current_time_before_requires_action_at | test_cb2_current_time_after_sla1 | test_cb2_current_time_after_sla2 | test_cb2_current_time_after_sla2 | test_cb2_current_time_within_sla1 |
    +--------------+-----------------------------------+-------------------------------------------------+----------------------------------+----------------------------------+----------------------------------+-----------------------------------+

    CB3
    +--------------+-----------------------------------+
    |              | CB3 Scheduled                     |
    |              | within 30m window                 |
    |              | AND                               |
    |              | call answered within 72 window    |
    +--------------+-----------------------------------+
    | SLA 1 missed |               FALSE               |
    +--------------+-----------------------------------+
    | SLA 2 missed |               FALSE               |
    +--------------+-----------------------------------+
    | test         | test_cb3_current_time_within_sla1 |
    +--------------+-----------------------------------+
    """
    # fmt: on

    def get_default_dt(self):
        return _make_datetime(year=2020, month=9, day=7, hour=9, minute=0)

    def get_requires_action_at(self):
        return self.now + datetime.timedelta(hours=1)

    def get_sla1_datetime(self):
        return self.get_requires_action_at() + datetime.timedelta(minutes=30)

    def get_sla2_datetime(self):
        return _make_datetime(year=2020, month=9, day=15, hour=12, minute=30)

    def test_current_time_before_requires_action_at(self):
        case = self.make_case(self.now, created=self.now)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create a callback that is due now 1 hour from now
        requires_action_at = self.get_requires_action_at()
        self.schedule_callback(case, user, created=self.now, requires_action_at=requires_action_at)

        # Move current time to 5 minute before requires_action_at
        self._move_time_forward(requires_action_at, minutes_forward=-5)
        # Generate report without a callback
        date_range = (self.now - datetime.timedelta(days=2), self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

        # Start a call
        self.start_call(case, user, self.now)
        # Generate report with a successful callback
        date_range = (self.now - datetime.timedelta(days=2), self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        # Contacting customer before the requires_action_at will result in a failure to meet SLA
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb2_current_time_before_requires_action_at(self):
        case = self.make_case(self.now, created=self.now)
        user = make_user()
        make_recipe("call_centre.operator", user=user)
        # Create CB1
        requires_action_at = self.get_requires_action_at()
        self.schedule_callback(case, user, created=self.now, requires_action_at=requires_action_at)

        # Move current time to 5 minute before requires_action_at
        self._move_time_forward(requires_action_at, minutes_forward=-5)

        # Create  CB2
        self.schedule_callback(case, user, created=self.now, requires_action_at=self.get_requires_action_at())

        # Generate report without a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

        # Start a call
        self.start_call(case, user, self.now)
        # Generate report with a successful callback
        date_range = (case.created, self.now + datetime.timedelta(days=2))
        values = self.get_report(date_range)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])


class MiSlaTestCasePhone(MiSlaTestCaseWeb):
    source = CASE_SOURCE.PHONE


class MiSlaTestCaseSMS(MiSlaTestCaseBase, TestCase):
    source = CASE_SOURCE.SMS

    # fmt: off
    """
    Rules used to determine if SLA1/SLA2 was missed
    Note: A callback attempt is when the operator has clicked the start call button after successfully contacting the user
    +-----------+--------------+-----------------------------------+--------------------------------------------------------------------+-------------------------------------------------------------------+
    |           |              | Callback attempted within 2 hours | Callback attempted after 2 hours AND current time within 8h window | Callback attempted after 2 hours AND current time after 8h window |
    +-----------+--------------+-----------------------------------+--------------------------------------------------------------------+-------------------------------------------------------------------+
    | SMS       | SLA 1 missed | FALSE                             | TRUE                                                               | TRUE                                                              |
    +-----------+--------------+-----------------------------------+--------------------------------------------------------------------+-------------------------------------------------------------------+
    |           | SLA 2 missed | FALSE                             | FALSE                                                              | TRUE                                                              |
    +-----------+--------------+-----------------------------------+--------------------------------------------------------------------+-------------------------------------------------------------------+
    | Voicemail | SLA 1 missed | FALSE                             | TRUE                                                               | TRUE                                                              |
    +-----------+--------------+-----------------------------------+--------------------------------------------------------------------+-------------------------------------------------------------------+
    |           | SLA 2 missed | FALSE                             | FALSE                                                              | TRUE                                                              |
    +-----------+--------------+-----------------------------------+--------------------------------------------------------------------+-------------------------------------------------------------------+
    """
    # fmt: on

    def get_default_dt(self):
        return _make_datetime(year=2020, month=9, day=7, hour=9, minute=0)

    def get_requires_action_at(self):
        return self.now + datetime.timedelta(hours=1)

    def get_sla1_datetime(self):
        return _make_datetime(year=2020, month=9, day=7, hour=11, minute=0)

    def get_sla2_datetime(self):
        return _make_datetime(year=2020, month=9, day=7, hour=17, minute=0)


class MiSlaTestCaseVoiceMail(MiSlaTestCaseSMS):
    source = CASE_SOURCE.VOICEMAIL
