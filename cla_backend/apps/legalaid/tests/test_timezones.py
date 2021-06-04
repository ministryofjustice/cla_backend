import pytz
from django.test import SimpleTestCase
from django.utils import timezone
from freezegun import freeze_time

from core.tests.mommy_utils import make_recipe


class BaseAssignedOutOfHours(object):
    def tearDown(self):
        self.freezer.stop()
        super(BaseAssignedOutOfHours, self).tearDown()

    def create_and_assign(self, dt):
        timezone_aware_dt = timezone.make_aware(dt, timezone.get_current_timezone())
        utc_dt = timezone_aware_dt.astimezone(pytz.utc)
        self.freezer = freeze_time(utc_dt)
        self.freezer.start()
        provider = make_recipe("cla_provider.provider")
        case = make_recipe("legalaid.case")
        case.assign_to_provider(provider)
        return case

    def test_before_hours(self):
        case = self.create_and_assign(self.dt.replace(hour=7, minute=30))
        self.assertTrue(case.assigned_out_of_hours)

    def test_first_hour_of_business(self):
        case = self.create_and_assign(self.dt.replace(hour=8, minute=30))
        self.assertFalse(case.assigned_out_of_hours)

    def test_second_hour_of_business(self):
        case = self.create_and_assign(self.dt.replace(hour=9, minute=30))
        self.assertFalse(case.assigned_out_of_hours)

    def test_last_hour_of_business(self):
        case = self.create_and_assign(self.dt.replace(hour=16, minute=30))
        self.assertFalse(case.assigned_out_of_hours)

    def test_after_hours(self):
        case = self.create_and_assign(self.dt.replace(hour=17, minute=30))
        self.assertTrue(case.assigned_out_of_hours)


class TestGMTAssignedOutOfHoursTestCase(BaseAssignedOutOfHours, SimpleTestCase):
    dt = timezone.datetime(2021, 2, 2)


class TestBSTAssignedOutOfHoursTestCase(BaseAssignedOutOfHours, SimpleTestCase):
    dt = timezone.datetime(2021, 5, 5)
