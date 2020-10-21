import datetime
import time
import mock
from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta, MO, TU

from core.tests.mommy_utils import make_recipe, make_user
from cla_eventlog import event_registry
from cla_eventlog.models import Log
from legalaid.forms import get_sla_time
from cla_eventlog.management.commands.add_72h_to_context import Command
from cla_common.call_centre_availability import OpeningHours


class Add72workingHoursToContextCommandTestCase(TestCase):
    def setUp(self):
        super(Add72workingHoursToContextCommandTestCase, self).setUp()
        self.instance = Command()

        hours = {
            "weekday": (datetime.time(9, 0), datetime.time(20, 0)),
            "saturday": (datetime.time(9, 0), datetime.time(12, 30)),
        }
        operator_hours = OpeningHours(**hours)
        from legalaid.utils import sla

        self.operator_hours_patcher = mock.patch.object(sla, "operator_hours", operator_hours)
        self.operator_hours_patcher.start()

    def tearDown(self):
        self.operator_hours_patcher.stop()

    def create_callback(self, requires_action_at):
        case = make_recipe("legalaid.case")
        user = make_user()
        make_recipe("call_centre.operator", user=user)
        event = event_registry.get_event("call_me_back")()
        event.get_log_code(case=case)
        log = event.process(
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
        return log

    def test_add_72h_to_context__updated_fields(self):
        now = datetime.datetime.now()
        now_tz = timezone.make_aware(now, timezone.get_default_timezone())
        log = self.create_callback(now_tz)
        self.assertNotIn("sla_72h", log.context)
        # Sleep for enough time to test modified hasn't changed
        time.sleep(3)
        self.instance.execute()
        log_updated = Log.objects.get(pk=log.pk)
        self.assertIn("sla_72h", log_updated.context)

        self.assertEqual(log.modified, log_updated.modified)

    @mock.patch("django.utils.timezone.now")
    @mock.patch("cla_common.call_centre_availability.current_datetime")
    def test_add_72h_to_context__sla_in_the_past(self, mock_common_datetime, timezone_mock):
        now = datetime.datetime(year=2020, month=10, day=5, hour=9, minute=0)
        expected = datetime.datetime(year=2020, month=10, day=13, hour=11, minute=30)
        expected = timezone.make_aware(expected, timezone.get_default_timezone())
        now_tz = timezone.make_aware(now, timezone.get_default_timezone())
        mock_common_datetime.return_value = now
        timezone_mock.return_value = now_tz
        log = self.create_callback(now_tz)
        self.assertNotIn("sla_72h", log.context)
        self.instance.execute()
        log = Log.objects.get(pk=log.pk)
        self.assertIn("sla_72h", log.context)
        self.assertEqual(log.context["sla_72h"], expected.isoformat())

    def get_last_monday(self):
        today = datetime.date.today()
        offset = -1
        if today.isoweekday() == 1:
            # If today is Monday then a offset of -1 will return today's date
            # so we need to use an offset of -2 in that case to get the previous monday
            offset = -2

        last_monday = today + relativedelta(weekday=MO(offset))
        return last_monday

    def get_next_tuesday(self):
        today = datetime.date.today()
        offset = +1
        if today.isoweekday() == 2:
            # If today is Tuesday then a offset of +1 will return today's date
            # so we need to use an offset of +2 in that case to get the next tuesday
            offset = +2

        next_tuesday = today + relativedelta(weekday=TU(offset))
        return next_tuesday

    @mock.patch("django.utils.timezone.now")
    @mock.patch("cla_common.call_centre_availability.current_datetime")
    @mock.patch("cla_common.call_centre_availability.bank_holidays", return_value=[])
    def test_add_72h_to_context__sla_in_the_future(self, mock_bank_holidays, mock_common_datetime, timezone_mock):
        now = datetime.datetime.combine(self.get_last_monday(), datetime.time(hour=9, minute=0))
        expected = datetime.datetime.combine(self.get_next_tuesday(), datetime.time(hour=11, minute=30))
        expected = timezone.make_aware(expected, timezone.get_default_timezone())
        now_tz = timezone.make_aware(now, timezone.get_default_timezone())
        mock_common_datetime.return_value = now
        timezone_mock.return_value = now_tz
        log = self.create_callback(now_tz)
        self.assertNotIn("sla_72h", log.context)
        self.instance.execute()
        log = Log.objects.get(pk=log.pk)
        self.assertIn("sla_72h", log.context)

        expected_str = expected.isoformat()
        if expected.utcoffset().total_seconds() == 0:
            # Strangely log.context["sla_72h"] falls in a 0 offset timezone
            # it does not include the timezone offset (should be 00:00Z)
            # so we have to set our expected datetime string representation to match it
            expected_str = expected.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertEqual(log.context["sla_72h"], expected_str)

        self.assertEqual(log.modified, log.modified)
