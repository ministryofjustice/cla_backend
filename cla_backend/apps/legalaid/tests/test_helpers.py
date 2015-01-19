import random
from django.test import TestCase
import datetime
from django.utils import timezone
from legalaid.forms import get_sla_time
import mock

class SLATimeHelperTestCase(TestCase):

    def _get_next_mon(self):
        now = timezone.now()
        mon = now + datetime.timedelta(days=7-now.weekday())
        return mon.replace(hour=10, minute=0, second=0, microsecond=0)

    def test_get_sla_time_simple_delta_works(self):
        with mock.patch('cla_common.call_centre_availability.bank_holidays', return_value=[]) as bank_hol:
            d = self._get_next_mon()
            self.assertEqual(get_sla_time(d, 15), d + datetime.timedelta(minutes=15))
            self.assertTrue(bank_hol.called)

    def test_get_sla_time_delta_past_end_of_weekday_works(self):
        with mock.patch('cla_common.call_centre_availability.bank_holidays', return_value=[]) as bank_hol:
            d = self._get_next_mon().replace(hour=19, minute=59)
            next_day = (d + datetime.timedelta(days=1)).replace(hour=9, minute=14)
            self.assertEqual(get_sla_time(d, 15), next_day)

            next_day_120 = next_day.replace(hour=10, minute=59)
            self.assertEqual(get_sla_time(d, 120), next_day_120)

            next_day_480 = next_day.replace(hour=16, minute=59)
            self.assertEqual(get_sla_time(d, 480), next_day_480)

            self.assertTrue(bank_hol.called)

    def test_get_sla_time_delta_past_end_of_saturday_works(self):
        with mock.patch('cla_common.call_centre_availability.bank_holidays', return_value=[]) as bank_hol:
            d = self._get_next_mon().replace(hour=12, minute=29)
            next_sat = (d + datetime.timedelta(days=5))
            next_mon = (next_sat + datetime.timedelta(days=2)).replace(hour=9, minute=14)
            self.assertEqual(get_sla_time(next_sat, 15), next_mon)
            self.assertTrue(bank_hol.called)

    def test_get_sla_time_delta_past_end_of_weekday_with_next_day_a_bank_hol_works(self):
        d = self._get_next_mon().replace(hour=19, minute=44)
        next_day = d + datetime.timedelta(days=1)
        next_day_as_bank_hol = datetime.datetime.combine(next_day, datetime.time())
        next_day_plus1 = (next_day + datetime.timedelta(days=1)).replace(hour=10, minute=44)
        next_day_plus1_480 = (next_day + datetime.timedelta(days=1)).replace(hour=16, minute=44)
        with mock.patch('cla_common.call_centre_availability.bank_holidays', return_value=[next_day_as_bank_hol]) as bank_hol:
            end_of_day = d.replace(hour=19, minute=59)
            self.assertEqual(get_sla_time(d, 15), end_of_day)
            self.assertEqual(get_sla_time(d, 120), next_day_plus1)
            self.assertEqual(get_sla_time(d, 480), next_day_plus1_480)
            self.assertTrue(bank_hol.called)


    def test_lots_of_dates_dont_break_it(self):
        with mock.patch('cla_common.call_centre_availability.bank_holidays', return_value=[]) as bank_hol:
            start_date = timezone.now().replace(hour=9, minute=0)

            dates = [start_date + datetime.timedelta(days=x) for x in range(1, 100)]
            for date in dates:
                random_hour = random.randint(9, 20)
                random_minute = random.randint(0, 59)
                date = date.replace(hour=random_hour, minute=random_minute)
                get_sla_time(date, 15)
                get_sla_time(date, 120)
                get_sla_time(date, 480)
                self.assertTrue(bank_hol.called)
