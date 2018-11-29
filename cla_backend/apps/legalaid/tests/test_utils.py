from datetime import date, datetime, time

from django.test import TestCase
from legalaid.utils.sla import is_in_business_hours

from cla_common.call_centre_availability import OpeningHours
from django.conf import settings


class SlaCustomBusinessHoursTestCase(TestCase):
    operator_hours = OpeningHours(**settings.OPERATOR_HOURS)

    xmas_eve = date(year=2018, month=12, day=24)
    xmas_eve_before_hours = datetime.combine(xmas_eve, time(hour=8, minute=59))
    xmas_eve_noon = datetime.combine(xmas_eve, time(hour=12))
    xmas_eve_last_minute = datetime.combine(xmas_eve, time(hour=17, minute=29))
    xmas_eve_after_hours = datetime.combine(xmas_eve, time(hour=18))

    new_years_eve = date(year=2018, month=12, day=31)
    new_years_eve_before_hours = datetime.combine(new_years_eve, time(hour=8, minute=59))
    new_years_eve_noon = datetime.combine(new_years_eve, time(hour=12))
    new_years_eve_last_minute = datetime.combine(new_years_eve, time(hour=17, minute=29))
    new_years_eve_after_hours = datetime.combine(new_years_eve, time(hour=18))

    def test_custom_business_hours(self):
        self.assertFalse(is_in_business_hours(self.xmas_eve_before_hours))
        self.assertTrue(is_in_business_hours(self.xmas_eve_noon))
        self.assertTrue(is_in_business_hours(self.xmas_eve_last_minute))
        self.assertFalse(is_in_business_hours(self.xmas_eve_after_hours))

        self.assertFalse(is_in_business_hours(self.new_years_eve_before_hours))
        self.assertTrue(is_in_business_hours(self.new_years_eve_noon))
        self.assertTrue(is_in_business_hours(self.new_years_eve_last_minute))
        self.assertFalse(is_in_business_hours(self.new_years_eve_after_hours))

    def test_custom_day_timeslots(self):
        slots = self.operator_hours.time_slots(self.xmas_eve)
        self.assertEquals(min(slots), datetime(2018, 12, 24, 9, 0))
        self.assertEquals(max(slots), datetime(2018, 12, 24, 17, 0))

        slots = self.operator_hours.time_slots(self.new_years_eve)
        self.assertEquals(min(slots), datetime(2018, 12, 31, 9, 0))
        self.assertEquals(max(slots), datetime(2018, 12, 31, 17, 0))
