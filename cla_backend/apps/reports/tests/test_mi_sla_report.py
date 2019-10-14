# coding=utf-8
from contextlib import contextmanager
import datetime
from django.test import TestCase
from django.utils import timezone
import mock

from core.tests.mommy_utils import make_recipe, make_user
from cla_eventlog import event_registry
from cla_eventlog.models import Log
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


class MiSlaTestCase(TestCase):
    @staticmethod
    def get_report(callback_minutes_after_window_start):
        dt = _make_datetime(2015, 1, 2, 9, 0, 0)
        with patch_field(Log, "created", dt + datetime.timedelta(minutes=1)):
            case = make_recipe("legalaid.case")

        user = make_user()
        make_recipe("call_centre.operator", user=user)

        event = event_registry.get_event("call_me_back")()
        with patch_field(Log, "created", dt + datetime.timedelta(minutes=1)):
            event.get_log_code(case=case)
            event.process(
                case, created_by=user, notes="", context={"requires_action_at": dt + datetime.timedelta(minutes=1)}
            )

        case.requires_action_at = dt
        case.save()

        event = event_registry.get_event("case")()
        with patch_field(Log, "created", dt + datetime.timedelta(minutes=callback_minutes_after_window_start)):
            event.process(case, status="call_started", created_by=user, notes="Call started")

        date_range = (_make_datetime(2015, 1, 1), _make_datetime(2015, 2, 1))

        with mock.patch("reports.forms.MICB1Extract.date_range", date_range):
            report = MICB1Extract()

            qs = report.get_queryset()
            headers = report.get_headers()

        return {k: v for k, v in zip(headers, qs[0])}

    def test_within_window(self):
        values = self.get_report(25)
        self.assertTrue(values["is_within_sla_1"])
        self.assertTrue(values["is_within_sla_2"])

    def test_after_window(self):
        values = self.get_report(35)
        self.assertFalse(values["is_within_sla_1"])
        self.assertTrue(values["is_within_sla_2"])

    def test_before_window(self):
        values = self.get_report(-5)
        self.assertFalse(values["is_within_sla_1"])
        self.assertTrue(values["is_within_sla_2"])

    def test_after_sla_2_limit(self):
        values = self.get_report(75 * 60)
        self.assertFalse(values["is_within_sla_1"])
        self.assertFalse(values["is_within_sla_2"])

    def test_before_sla_2_limit(self):
        values = self.get_report(-75 * 60)
        self.assertFalse(values["is_within_sla_1"])
        self.assertFalse(values["is_within_sla_2"])
