from unittest import TestCase
from django.utils import timezone
from cla_common.constants import CALLBACK_TYPES
from core.tests.mommy_utils import make_recipe
import datetime
from checker.utils import get_timeslot_of_datetime, callback_capacity_threshold_breached


class TestGetTimeslotOfDate(TestCase):
    CALLBACK_TIME_SLOT = "checker.callback_time_slot"

    @staticmethod
    def get_no_capacity_slots(dt):
        return [
            {"date": dt.date(), "capacity": 0, "time": "0900"},
            {"date": dt.date(), "capacity": 0, "time": "0930"},
            {"date": dt.date(), "capacity": 0, "time": "1000"},
            {"date": dt.date(), "capacity": 0, "time": "1030"},
            {"date": dt.date(), "capacity": 0, "time": "1100"},
            {"date": dt.date(), "capacity": 0, "time": "1130"},
            {"date": dt.date(), "capacity": 0, "time": "1200"},
            {"date": dt.date(), "capacity": 0, "time": "1230"},
            {"date": dt.date(), "capacity": 0, "time": "1300"},
            {"date": dt.date(), "capacity": 0, "time": "1330"},
            {"date": dt.date(), "capacity": 0, "time": "1400"},
            {"date": dt.date(), "capacity": 0, "time": "1430"},
            {"date": dt.date(), "capacity": 0, "time": "1500"},
            {"date": dt.date(), "capacity": 0, "time": "1530"},
            {"date": dt.date(), "capacity": 0, "time": "1600"},
            {"date": dt.date(), "capacity": 0, "time": "1630"},
            {"date": dt.date(), "capacity": 0, "time": "1700"},
            {"date": dt.date(), "capacity": 0, "time": "1730"},
            {"date": dt.date(), "capacity": 1, "time": "1800"},
            {"date": dt.date(), "capacity": 0, "time": "1830"},
            {"date": dt.date(), "capacity": 0, "time": "1900"},
            {"date": dt.date(), "capacity": 0, "time": "1930"},
        ]

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
        slots = self.get_no_capacity_slots(dt)
        for slot in slots:
            if slot["time"] == "1800":
                slot["capacity"] = 1
        self._create_callback_capacity_slots(slots)
        self._create_callback(dt.replace(hour=18, minute=0))
        self.assertTrue(callback_capacity_threshold_breached(dt))

    def test_date_breached_threshold_from_previous_week(self):
        dt = datetime.datetime(2024, 4, 3, 15, 59, 0, 0).replace(tzinfo=timezone.utc)
        previous_week = dt - datetime.timedelta(weeks=1)
        slots = self.get_no_capacity_slots(dt)
        for slot in slots:
            if slot["time"] == "1800":
                slot["capacity"] = 1
                slot["date"] = previous_week.date()
        self._create_callback_capacity_slots(slots)
        self._create_callback(dt.replace(hour=18, minute=0))
        self.assertTrue(callback_capacity_threshold_breached(dt))

    def test_date_breached_not_threshold(self):
        dt = datetime.datetime(2024, 4, 4, 15, 59, 0, 0).replace(tzinfo=timezone.utc)
        slots = self.get_no_capacity_slots(dt)
        for slot in slots:
            if slot["time"] == "1800":
                slot["capacity"] = 2
        self._create_callback_capacity_slots(slots)
        self._create_callback(dt.replace(hour=18, minute=0))
        self.assertFalse(callback_capacity_threshold_breached(dt))

    def test_date_breached_not_threshold_from_previous_week(self):
        dt = datetime.datetime(2024, 4, 5, 15, 59, 0, 0).replace(tzinfo=timezone.utc)
        previous_week = dt - datetime.timedelta(weeks=1)
        slots = self.get_no_capacity_slots(dt)
        for slot in slots:
            if slot["time"] == "1800":
                slot["capacity"] = 2
                slot["date"] = previous_week.date()
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
