from unittest import TestCase
from django.utils import timezone
from cla_common.constants import CALLBACK_TYPES
from core.tests.mommy_utils import make_recipe
import datetime
from checker.helpers import get_timeslot_of_datetime, callback_capacity_threshold_breached


class TestGetTimeslotOfDate(TestCase):
    CALLBACK_TIME_SLOT = "checker.callback_time_slot"

    def test_get_timeslot(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=5, date=tomorrow, time="0900")
        self.assertEqual(
            get_timeslot_of_datetime(datetime.datetime.combine(tomorrow, datetime.time(9, 0))).capacity, 5
        )

    def test_no_timeslot(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        self.assertIsNone(get_timeslot_of_datetime(datetime.datetime.combine(tomorrow, datetime.time(10, 0))))

    def test_date_breached_threshold(self):
        dt = datetime.datetime(2024, 4, 3, 15, 59, 0, 0).replace(tzinfo=timezone.utc)
        slots = [
            {"date": dt.date(), "capacity": 1, "time": "1800"},
            {"date": dt.date(), "capacity": 0, "time": "1830"},
            {"date": dt.date(), "capacity": 0, "time": "1900"},
            {"date": dt.date(), "capacity": 0, "time": "1930"},
        ]
        self._create_callback_capacity_slots(slots)
        self._create_callback(dt.replace(hour=18, minute=0))
        self.assertTrue(callback_capacity_threshold_breached(dt))

    def test_date_breached_threshold_from_previous_week(self):
        dt = datetime.datetime(2024, 4, 3, 15, 59, 0, 0).replace(tzinfo=timezone.utc)
        previous_week = dt - datetime.timedelta(weeks=1)
        slots = [
            {"date": previous_week.date(), "capacity": 1, "time": "1800"},
            {"date": dt.date(), "capacity": 0, "time": "1830"},
            {"date": dt.date(), "capacity": 0, "time": "1900"},
            {"date": dt.date(), "capacity": 0, "time": "1930"},
        ]
        self._create_callback_capacity_slots(slots)
        self._create_callback(dt.replace(hour=18, minute=0))
        self.assertTrue(callback_capacity_threshold_breached(dt))

    def test_date_breached_not_threshold(self):
        dt = datetime.datetime(2024, 4, 4, 15, 59, 0, 0).replace(tzinfo=timezone.utc)
        slots = [
            {"date": dt.date(), "capacity": 2, "time": "1800"},
            {"date": dt.date(), "capacity": 0, "time": "1830"},
            {"date": dt.date(), "capacity": 0, "time": "1900"},
            {"date": dt.date(), "capacity": 0, "time": "1930"},
        ]
        self._create_callback_capacity_slots(slots)
        self._create_callback(dt.replace(hour=18, minute=0))
        self.assertFalse(callback_capacity_threshold_breached(dt))

    def test_date_breached_not_threshold_from_previous_week(self):
        dt = datetime.datetime(2024, 4, 5, 15, 59, 0, 0).replace(tzinfo=timezone.utc)
        previous_week = dt - datetime.timedelta(weeks=1)
        slots = [
            {"date": previous_week.date(), "capacity": 2, "time": "1800"},
            {"date": dt.date(), "capacity": 0, "time": "1830"},
            {"date": dt.date(), "capacity": 0, "time": "1900"},
            {"date": dt.date(), "capacity": 0, "time": "1930"},
        ]
        self._create_callback_capacity_slots(slots)
        self._create_callback(dt.replace(hour=18, minute=0))
        self.assertFalse(callback_capacity_threshold_breached(dt))

    def test_no_callback_capacity(self):
        dt = datetime.datetime(2024, 4, 2, 15, 59, 0, 0).replace(tzinfo=timezone.utc)
        self._create_callback(dt.replace(hour=18, minute=0))
        self.assertFalse(callback_capacity_threshold_breached(dt))

    def _create_callback_capacity_slots(self, slots):
        for slot in slots:
            make_recipe(self.CALLBACK_TIME_SLOT, **slot)

    def _create_callback(self, requires_action_at):
        make_recipe("legalaid.case", requires_action_at=requires_action_at, callback_type=CALLBACK_TYPES.CHECKER_SELF)
