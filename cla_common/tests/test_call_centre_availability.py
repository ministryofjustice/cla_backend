from datetime import datetime, time
import unittest
from contextlib import contextmanager
from .. import call_centre_availability
from ..call_centre_availability import available, time_slots, Hours, OpeningHours


class MonkeyPatch(object):
    def __init__(self, obj, attr, value):
        self.obj = obj
        self.attr = attr
        self.applied = False

        if hasattr(obj, attr):
            self.original = getattr(obj, attr)
            setattr(obj, attr, value)
            self.applied = True

    def undo(self):
        if self.applied:
            setattr(self.obj, self.attr, self.original)


@contextmanager
def override_current_time(dt):
    override = lambda: dt
    patch = MonkeyPatch(call_centre_availability, "current_datetime", override)
    yield
    patch.undo()


def mock_bank_holidays():
    return [datetime(2014, 12, 25, 0, 0)]


TEST_OPENING_HOURS = OpeningHours(weekday=(time(9, 0), time(20, 0)), saturday=(time(9, 0), time(12, 30)))


def pretty(time):
    return "{0:%a, %d %b %I:%M %p}".format(time)


class CallCentreAvailabilityTestCase(unittest.TestCase):
    def setUp(self):
        self.bank_holiday_patch = MonkeyPatch(call_centre_availability, "bank_holidays", mock_bank_holidays)
        self.now = datetime(2014, 10, 22, 9, 0)

    def tearDown(self):
        self.bank_holiday_patch.undo()

    def assertAvailable(self, time):
        fail_msg = "{0} is not available at {1}".format(pretty(time), pretty(self.now))
        with override_current_time(self.now):
            self.assertTrue(available(time), fail_msg)

    def assertNotAvailable(self, time):
        fail_msg = "{0} is available at {1}".format(pretty(time), pretty(self.now))
        with override_current_time(self.now):
            self.assertFalse(available(time), fail_msg)

    def assertDateEqual(self, dt1, dt2):
        self.assertEqual(dt1.date(), dt2.date())

    def assertTimeEqual(self, dt1, dt2):
        self.assertEqual(dt1.time(), dt2.time())

    def test_weekday_9am(self):
        self.assertAvailable(datetime(2014, 10, 23, 9, 0))

    def test_weekday_before_9am(self):
        self.assertNotAvailable(datetime(2014, 10, 23, 7, 0))

    def test_weekday_after_8pm(self):
        self.assertNotAvailable(datetime(2014, 10, 23, 21, 0))

    def test_saturday(self):
        self.assertAvailable(datetime(2014, 10, 25, 10, 15))
        self.assertNotAvailable(datetime(2014, 10, 25, 12, 30))

    def test_sunday(self):
        self.assertNotAvailable(datetime(2014, 10, 26, 9, 0))

    def test_bank_holiday(self):
        self.assertNotAvailable(datetime(2014, 12, 25, 9, 0))

    def test_boxing_day_2020(self):
        self.assertNotAvailable(datetime(2020, 12, 26, 9, 0))

    def test_time_slots(self):
        with override_current_time(self.now):
            slots = time_slots(datetime(2014, 10, 23).date())
            self.assertEqual(slots[0], datetime(2014, 10, 23, 9, 0))
            map(lambda slot: self.assertTrue(available(slot)), slots)

    def test_no_availability(self):
        self.now = datetime(2014, 10, 25, 13, 0)
        with override_current_time(self.now):
            slots = time_slots(self.now.date())
            self.assertEqual(len(slots), 0)

    def test_hours_class(self):
        hours = Hours(time(9, 0), time(20, 0))
        self.assertTrue(hours)
        self.assertFalse(hours.is_empty())

        self.assertTrue(self.now in hours)

        after_8pm = datetime(2014, 10, 23, 22, 0)
        self.assertFalse(after_8pm in hours)

        before_9am = datetime(2014, 10, 24, 7, 0)
        self.assertFalse(before_9am in hours)

    def test_empty_hours_class(self):
        hours = Hours(None, None)
        self.assertFalse(hours)
        self.assertTrue(hours.is_empty())

        self.assertFalse(self.now in hours)

    def test_openinghours_class(self):
        openinghours = TEST_OPENING_HOURS

        bank_holiday_9am = datetime(2014, 12, 25, 9, 0)
        self.assertFalse(bank_holiday_9am in openinghours)

        sunday_morning = datetime(2014, 10, 26, 10, 0)
        self.assertFalse(sunday_morning in openinghours)

        saturday_after_1230pm = datetime(2014, 10, 25, 12, 30)
        self.assertFalse(saturday_after_1230pm in openinghours)

        friday_afternoon = datetime(2014, 10, 24, 13, 0)
        self.assertTrue(friday_afternoon in openinghours)

    def test_available_days(self):
        expected_days = [
            datetime(2014, 10, 23),
            datetime(2014, 10, 24),
            datetime(2014, 10, 25),
            # 26th is a sunday
            datetime(2014, 10, 27),
            datetime(2014, 10, 28),
            datetime(2014, 10, 29),
        ]

        with override_current_time(self.now):
            openinghours = TEST_OPENING_HOURS
            days = openinghours.available_days()
            for expected, actual in zip(expected_days, days):
                self.assertDateEqual(expected, actual)

    def test_today_slots(self):
        expected_slots = [datetime(2014, 10, 25, 11, 30), datetime(2014, 10, 25, 12, 0)]

        with override_current_time(datetime(2014, 10, 25, 9, 30)):
            openinghours = TEST_OPENING_HOURS
            slots = openinghours.today_slots()
            self.assertEqual(len(expected_slots), len(slots))
            for expected, actual in zip(expected_slots, slots):
                self.assertTimeEqual(expected, actual)

    def test_provider_hours(self):
        fake_now = datetime(2099, 1, 1, 12, 0)
        with override_current_time(fake_now):
            PROVIDER_HOURS = {"weekday": (time(9, 0), time(17, 0))}

            OH = OpeningHours(**PROVIDER_HOURS)
            self.assertTrue(fake_now in OH)

    def test_day_override(self):
        with override_current_time(self.now):
            opening_hours_no_thurs = OpeningHours(weekday=(time(9, 0), time(17, 0)), thursday=(None, None))
            self.assertTrue(opening_hours_no_thurs.available(self.now))

            opening_hours_no_weds = OpeningHours(weekday=(time(9, 0), time(17, 0)), wednesday=(None, None))
            self.assertFalse(opening_hours_no_weds.available(self.now))
