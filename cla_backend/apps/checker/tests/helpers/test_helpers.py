from unittest import TestCase
from core.tests.mommy_utils import make_recipe
import datetime as dt
from checker.helpers import get_timeslot_of_datetime


class TestGetTimeslotOfDate(TestCase):
    CALLBACK_TIME_SLOT = "checker.callback_time_slot"

    def test_get_timeslot(self):
        tomorrow = dt.datetime.today() + dt.timedelta(days=1)
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=5, date=tomorrow, time="0900")
        self.assertEqual(get_timeslot_of_datetime(dt.datetime.combine(tomorrow, dt.time(9, 0))).capacity, 5)

    def test_no_timeslot(self):
        tomorrow = dt.datetime.today() + dt.timedelta(days=1)
        self.assertIsNone(get_timeslot_of_datetime(dt.datetime.combine(tomorrow, dt.time(10, 0))))
