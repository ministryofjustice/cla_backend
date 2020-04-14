# coding=utf-8
from contextlib import contextmanager
import datetime
from django.test import TestCase
from django.utils import timezone
import mock

from cla_common.constants import CASE_SOURCE

from core.tests.mommy_utils import make_recipe, make_user
from cla_eventlog import event_registry
from cla_eventlog.models import Log
from legalaid.forms import get_sla_time
from reports.forms import MICB1Extract
from legalaid.models import Case


def _make_datetime(year=None, month=None, day=None, hour=0, minute=0, second=0):
    today = datetime.date.today()
    year = year if year else today.year
    month = month if month else today.month
    day = day if day else today.day
    dt = datetime.datetime(year, month, day, hour, minute, second)
    tz = timezone.get_current_timezone()
    return timezone.make_aware(dt, tz)


def mock_now(dt):
    return dt


@contextmanager
def patch_field(cls, field_name, dt):
    field = cls._meta.get_field(field_name)
    with mock.patch.object(field, "default", new=mock_now(dt)):
        yield


class MiSlaTestCaseBase(TestCase):
    source = None
    requires_action_at_minutes_offset = 60

    def make_case(self, dt):
        with patch_field(Log, "created", dt - datetime.timedelta(minutes=1)):
            return make_recipe("legalaid.case", source=self.source)

    def schedule_callback(self, case, user, created, requires_action_at=None):
        requires_action_at = requires_action_at or created + datetime.timedelta(minutes=35)
        event = event_registry.get_event("call_me_back")()
        with patch_field(Log, "created", created):
            event.get_log_code(case=case)
            event.process(
                case,
                created_by=user,
                notes="",
                context={
                    "requires_action_at": requires_action_at,
                    "sla_15": get_sla_time(requires_action_at, 15),
                    "sla_30": get_sla_time(requires_action_at, 30),
                    "sla_120": get_sla_time(requires_action_at, 120),
                    "sla_480": get_sla_time(requires_action_at, 480),
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


class MiSlaTestCaseWeb(MiSlaTestCaseBase):
    source = CASE_SOURCE.WEB

    def test_call_answered_within_sla1_window(self):
        values = self.create_and_get_report(25)
        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_call_answered_after_sla1_window(self):
        values = self.create_and_get_report(35)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_call_answered_before_sla1_window(self):
        values = self.create_and_get_report(-5)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_call_answered_after_sla2_window(self):
        values = self.create_and_get_report(75 * 60)
        self.assertTrue(values["missed_sla_1"])
        self.assertTrue(values["missed_sla_2"])

    def test_cb1_uncalled_and_current_time_before_sla1(self):
        # SLA 1 miss is FALSE - Current time before SLA1 window
        # SLA 2 miss is FALSE - Current time is within sla2 window

        # 9:01 tomorrow
        created = _make_datetime(hour=9, minute=1) + datetime.timedelta(days=1)
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1
        requires_action_at = created + datetime.timedelta(hours=1)
        self.schedule_callback(case, user, created, requires_action_at)

        date_range = (created - datetime.timedelta(days=2), created + datetime.timedelta(days=2))
        values = self.get_report(date_range)

        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb1_uncalled_and_current_time_after_sla1(self):
        # SLA 1 miss is TRUE - Current time is after SLA1 window and CB2 hasn't been scheduled
        # SLA 2 miss is FALSE - Current time is within sla2 window

        # 9:01 yesterday
        created = _make_datetime(hour=9, minute=1) - datetime.timedelta(days=1)
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1
        requires_action_at = created + datetime.timedelta(hours=1)
        self.schedule_callback(case, user, created, requires_action_at)

        date_range = (created - datetime.timedelta(days=2), created + datetime.timedelta(days=2))
        values = self.get_report(date_range)

        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb2_created_before_sla1_and_current_time_before_sla1(self):
        # SLA 1 miss is TRUE - CB2 is created before SLA1 window
        # SLA 2 miss is FALSE - Current time is within sla2 window

        # 9:01 tomorrow
        created = _make_datetime(hour=9, minute=1) + datetime.timedelta(days=1)
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1
        requires_action_at = created + datetime.timedelta(hours=3)
        self.schedule_callback(case, user, created, requires_action_at)

        # Create CB 2 before SLA1 window
        cb2_created = requires_action_at + datetime.timedelta(minutes=-20)
        self.schedule_callback(case, user, created, cb2_created)

        date_range = (created - datetime.timedelta(days=2), created + datetime.timedelta(days=2))
        values = self.get_report(date_range)

        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb2_created_WITHIN_sla1_window_and_current_time_WITHIN_sla2_window(self):
        # SLA 1 miss is FALSE - CB2 created within sla1 window
        # SLA 2 miss is FALSE - Current time is within sla2 window

        # 9:01 yesterday
        created = _make_datetime(hour=9, minute=1) - datetime.timedelta(days=1)
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1
        requires_action_at = created + datetime.timedelta(hours=1)
        self.schedule_callback(case, user, created, requires_action_at)

        # Create CB2 within SLA1 window
        self.schedule_callback(case, user, requires_action_at + datetime.timedelta(minutes=25))

        date_range = (created - datetime.timedelta(days=2), created + datetime.timedelta(days=1))
        values = self.get_report(date_range)

        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb2_created_BEFORE_sla1_window_and_current_time_WITHIN_sla2_window(self):
        # SLA 1 miss is TRUE - CB2 created before sla1 window
        # SLA 2 miss is FALSE - Current time is within sla2 window

        # 9:01 yesterday
        created = _make_datetime(hour=9, minute=1) - datetime.timedelta(days=1)
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1
        requires_action_at = created + datetime.timedelta(hours=1)
        self.schedule_callback(case, user, created, requires_action_at)

        # Create CB2 before SLA1 window
        self.schedule_callback(case, user, requires_action_at + datetime.timedelta(minutes=-5))

        date_range = (created - datetime.timedelta(days=2), created + datetime.timedelta(days=1))
        values = self.get_report(date_range)

        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb2_created_AFTER_sla1_window_and_current_time_WITHIN_sla2_window(self):
        # SLA 1 miss is TRUE  - CB2 created after sla1 window
        # SLA 2 miss is FALSE - Current time is within sla2 window

        # 9:01 yesterday
        created = _make_datetime(hour=9, minute=1) - datetime.timedelta(days=1)
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB1
        requires_action_at = created + datetime.timedelta(hours=1)
        self.schedule_callback(case, user, created, requires_action_at)

        # Create CB2 after SLA1 window
        self.schedule_callback(case, user, requires_action_at + datetime.timedelta(minutes=31))

        date_range = (created - datetime.timedelta(days=2), created + datetime.timedelta(days=1))
        values = self.get_report(date_range)

        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb2_created_AFTER_sla1_window_and_current_time_AFTER_sla2_window(self):
        # SLA 1 miss is TRUE  - CB2 created after sla1 window
        # SLA 2 miss is TRUE  - Current time is after sla2 window

        # 9:01 4 days ago
        created = _make_datetime(hour=9, minute=1) - datetime.timedelta(days=4)
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1
        requires_action_at = created + datetime.timedelta(hours=1)
        self.schedule_callback(case, user, created, requires_action_at)

        # Create CB2 after SLA1 window
        self.schedule_callback(case, user, requires_action_at + datetime.timedelta(minutes=31))

        date_range = (created - datetime.timedelta(days=5), created + datetime.timedelta(days=5))
        values = self.get_report(date_range)

        self.assertTrue(values["missed_sla_1"])
        self.assertTrue(values["missed_sla_2"])

    def test_cb2_created_WITHIN_sla1_window_and_call_answered_WITHIN_sla2_window(self):
        # SLA 1 miss is FALSE  - CB2 created within sla1 window
        # SLA 2 miss is FALSE  - Call answered within SLA2 window
        created = _make_datetime(2015, 1, 2, 9, 1, 0)
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1
        requires_action_at = created + datetime.timedelta(hours=1)
        self.schedule_callback(case, user, created, requires_action_at)

        # Create CB2 within SLA1 window
        self.schedule_callback(case, user, requires_action_at + datetime.timedelta(minutes=25))

        # Start call
        self.start_call(case, user, requires_action_at + datetime.timedelta(minutes=60))

        date_range = (_make_datetime(2015, 1, 1), _make_datetime(2015, 2, 1))
        values = self.get_report(date_range)

        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb3_created_WITHIN_sla1_window_and_call_answered_WITHIN_sla2_window(self):
        # SLA 1 miss is FALSE  - CB3 created within sla1 window
        # SLA 2 miss is FALSE  - Call answered within SLA2 window
        created = _make_datetime(2015, 1, 2, 9, 1, 0)
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1
        requires_action_at = created + datetime.timedelta(hours=1)
        self.schedule_callback(case, user, created, requires_action_at)

        # Create CB2 within SLA1 window
        self.schedule_callback(case, user, requires_action_at + datetime.timedelta(minutes=25))

        # Create CB3 within SLA1 window
        self.schedule_callback(case, user, requires_action_at + datetime.timedelta(minutes=28))

        # Start call
        self.start_call(case, user, requires_action_at + datetime.timedelta(minutes=60 * 60))

        date_range = (_make_datetime(2015, 1, 1), _make_datetime(2015, 2, 1))
        values = self.get_report(date_range)

        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])


class MiSlaTestCasePhone(MiSlaTestCaseWeb):
    source = CASE_SOURCE.PHONE


class MiSlaTestCaseSMS(MiSlaTestCaseBase):
    source = CASE_SOURCE.SMS

    def make_case(self, dt):
        with patch_field(Case, "created", dt - datetime.timedelta(minutes=2)):
            return super(MiSlaTestCaseSMS, self).make_case(dt)

    def test_call_answered_within_sla1_window(self):
        # To meet SLA1 SMS and Voice mail cases need to contacted two hours from the case creation and not the
        # 2 hours from the callback time https://dsdmoj.atlassian.net/browse/LGA-1051
        created = _make_datetime(2015, 1, 2, 9, 1, 0)
        case = self.make_case(created)
        # 90 minutes from case creation (30 + self.requires_action_at_minutes_offset)
        # is still within the 2 hours for SLA1
        values = self.create_and_get_report(30, case=case)
        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_call_answered_after_sla1_window(self):
        # To meet SLA1 SMS and Voice mail cases need to contacted two hours from the case creation and not the
        # 2 hours from the callback time https://dsdmoj.atlassian.net/browse/LGA-1051
        created = _make_datetime(2015, 1, 2, 9, 1, 0)
        case = self.make_case(created)
        # 125 minutes from case creation (65 + self.requires_action_at_minutes_offset)
        # is outside of SlA1
        values = self.create_and_get_report(65, case=case)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_uncalled_and_current_time_within_sla1(self):
        # SLA 1 miss is FALSE - Current time before SLA1 window
        # SLA 2 miss is FALSE - Current time is within sla2 window

        # Create the case 1 hour ago
        today = datetime.datetime.now()
        created = _make_datetime(hour=today.hour, minute=today.minute, second=today.second) - datetime.timedelta(
            hours=1
        )
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1 after 10 minutes of creating the case
        requires_action_at = created + datetime.timedelta(minutes=10)
        self.schedule_callback(case, user, created, requires_action_at)

        date_range = (created, created + datetime.timedelta(hours=1))
        values = self.get_report(date_range)

        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_uncalled_and_current_time_after_sla1(self):
        # SLA 1 miss is TRUE - Uncalled and Current time is after SLA1 window
        # SLA 2 miss is FALSE - Uncalled BUT Current time is within sla2 window

        # Create the case 2 hours and 10 minutes ago
        today = datetime.datetime.now()
        created = _make_datetime(hour=today.hour, minute=today.minute, second=today.second) - datetime.timedelta(
            hours=2, minutes=10
        )
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1 after 8 minutes of creating the case
        requires_action_at = created + datetime.timedelta(minutes=8)
        self.schedule_callback(case, user, created, requires_action_at)

        date_range = (created, created + datetime.timedelta(hours=3))
        values = self.get_report(date_range)

        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_uncalled_and_current_time_within_sla2(self):
        # SLA 1 miss is TRUE - Uncalled and Current time is after SLA1
        # SLA 2 miss is FALSE - Uncalled BUT Current time is within SLA2
        # Create the case 7 hour ago
        today = datetime.datetime.now()
        created = _make_datetime(hour=today.hour, minute=today.minute, second=today.second) - datetime.timedelta(
            hours=7
        )
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1 after 60 minutes of creating the case
        requires_action_at = created + datetime.timedelta(minutes=8)
        self.schedule_callback(case, user, created, requires_action_at)

        date_range = (created, created + datetime.timedelta(hours=7))
        values = self.get_report(date_range)

        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_uncalled_and_current_time_after_sla2(self):
        # SLA 1 miss is TRUE - Uncalled and Current time is after SLA1
        # SLA 2 miss is TRUE - Uncalled and Current time is after SLA2

        # Create the case 9 hour ago
        today = datetime.datetime.now()
        created = _make_datetime(hour=today.hour, minute=today.minute, second=today.second) - datetime.timedelta(
            hours=9
        )
        case = self.make_case(created)
        user = make_user()
        make_recipe("call_centre.operator", user=user)

        # Create CB 1 after 60 minutes of creating the case
        requires_action_at = created + datetime.timedelta(minutes=8)
        self.schedule_callback(case, user, created, requires_action_at)

        date_range = (created, created + datetime.timedelta(hours=9))
        values = self.get_report(date_range)

        self.assertTrue(values["missed_sla_1"])
        self.assertTrue(values["missed_sla_2"])


class MiSlaTestCaseVoiceMail(MiSlaTestCaseBase):
    source = CASE_SOURCE.VOICEMAIL
