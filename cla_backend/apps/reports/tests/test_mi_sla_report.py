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


def _make_datetime(year, month, day, hour=0, minute=0, second=0):
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

    def get_report(self, callback_minutes_after, callback_attempt=0):
        dt = _make_datetime(2015, 1, 2, 9, 1, 0)
        with patch_field(Log, "created", dt - datetime.timedelta(minutes=1)):
            case = make_recipe("legalaid.case", source=self.source)

        user = make_user()
        make_recipe("call_centre.operator", user=user)

        requires_action_act = dt
        while callback_attempt >= 0:
            event = event_registry.get_event("call_me_back")()
            with patch_field(Log, "created", requires_action_act):
                event.get_log_code(case=case)
                event.process(
                    case,
                    created_by=user,
                    notes="",
                    context={
                        "requires_action_at": requires_action_act,
                        "sla_15": get_sla_time(dt, 15),
                        "sla_30": get_sla_time(dt, 30),
                        "sla_120": get_sla_time(dt, 120),
                        "sla_480": get_sla_time(dt, 480),
                    },
                )
                case.set_requires_action_at(requires_action_act)

            event = event_registry.get_event("case")()
            requires_action_act = requires_action_act + datetime.timedelta(minutes=callback_minutes_after)
            with patch_field(Log, "created", requires_action_act):
                event.process(case, status="call_started", created_by=user, notes="Call started")
            requires_action_act = requires_action_act + datetime.timedelta(minutes=30, seconds=30)

            callback_attempt = callback_attempt - 1

        date_range = (_make_datetime(2015, 1, 1), _make_datetime(2015, 2, 1))

        with mock.patch("reports.forms.MICB1Extract.date_range", date_range):
            report = MICB1Extract()

            qs = report.get_queryset()
            headers = report.get_headers()

        return {k: v for k, v in zip(headers, qs[0])}


class MiSlaTestCaseWeb(MiSlaTestCaseBase):
    source = CASE_SOURCE.WEB

    def test_within_window(self):
        values = self.get_report(25)
        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_after_window(self):
        values = self.get_report(35)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_before_window(self):
        values = self.get_report(-5)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_after_sla_2_limit(self):
        values = self.get_report(75 * 60)
        self.assertTrue(values["missed_sla_1"])
        self.assertTrue(values["missed_sla_2"])

    def test_before_sla_2_limit(self):
        values = self.get_report(-75 * 60)
        self.assertTrue(values["missed_sla_1"])
        self.assertTrue(values["missed_sla_2"])

    def test_within_cb2_window(self):
        values = self.get_report(35, callback_attempt=1)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_cb2_after_sla_2_limit(self):
        values = self.get_report(75 * 60, callback_attempt=1)
        self.assertTrue(values["missed_sla_1"])
        self.assertTrue(values["missed_sla_2"])

    def test_within_cb3_window(self):
        values = self.get_report(70, callback_attempt=2)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])


class MiSlaTestCasePhone(MiSlaTestCaseBase):
    source = CASE_SOURCE.PHONE

    def test_within_two_hours(self):
        values = self.get_report(90)
        self.assertFalse(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_within_eight_hours(self):
        values = self.get_report(4 * 60)
        self.assertTrue(values["missed_sla_1"])
        self.assertFalse(values["missed_sla_2"])

    def test_beyond_eight_working_hours(self):
        values = self.get_report(24 * 60)
        self.assertTrue(values["missed_sla_1"])
        self.assertTrue(values["missed_sla_2"])
