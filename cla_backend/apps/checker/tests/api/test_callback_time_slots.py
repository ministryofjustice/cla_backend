import mock
import datetime as dt
from rest_framework.test import APITestCase
from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin
from legalaid.tests.views.test_base import CLACheckerAuthBaseApiTestMixin
from checker.call_centre_availability import get_available_slots


class CallbackTimeSlotsTestCase(SimpleResourceAPIMixin, CLACheckerAuthBaseApiTestMixin, APITestCase):
    LOOKUP_KEY = "id"
    API_URL_BASE_NAME = "callback_time_slots"
    CALLBACK_TIME_SLOT = "checker.callback_time_slot"
    LEGALAID_CASE = "legalaid.case"

    def setup_resources(self):
        pass

    # Make sure all times are available
    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_slots(self, _):
        # Create callback time slots with capacity
        tomorrow = dt.datetime.today() + dt.timedelta(days=1)
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=2, date=tomorrow, time="0900")
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=1, date=tomorrow, time="1000")
        # This callback has no capacity so it should not be bookable
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=0, date=tomorrow, time="1100")
        slots = get_available_slots(num_days=2)
        self.assertIn(dt.datetime.combine(tomorrow, dt.time(hour=9, minute=0)), slots)
        self.assertIn(dt.datetime.combine(tomorrow, dt.time(hour=10, minute=0)), slots)
        self.assertNotIn(dt.datetime.combine(tomorrow, dt.time(hour=11, minute=0)), slots)

        # Book a callback for 10am tomorrow. 10am slot only has a capacity of 1, after this it should not be available
        requires_action_at = dt.datetime.combine(tomorrow, dt.time(hour=10, minute=0))
        make_recipe(self.LEGALAID_CASE, requires_action_at=requires_action_at)
        slots = get_available_slots(num_days=2)
        self.assertIn(dt.datetime.combine(tomorrow, dt.time(hour=9, minute=0)), slots)
        self.assertNotIn(dt.datetime.combine(tomorrow, dt.time(hour=10, minute=0)), slots)

    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_negative_capacity(self, _):
        # This handles the case where an operator overrides the capacity rules and the capacity becomes negative.
        tomorrow = dt.datetime.today() + dt.timedelta(days=1)
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=1, date=tomorrow, time="0900")
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=1, date=tomorrow, time="1000")

        slots = get_available_slots(num_days=2)
        self.assertIn(dt.datetime.combine(tomorrow, dt.time(9, 0)), slots)
        self.assertIn(dt.datetime.combine(tomorrow, dt.time(10, 0)), slots)

        # Book two callbacks for 10am tomorrow, this should make the capacity negative
        requires_action_at = dt.datetime.combine(tomorrow, dt.time(hour=10, minute=0))
        for _ in range(2):
            make_recipe(self.LEGALAID_CASE, requires_action_at=requires_action_at)
        slots = get_available_slots(num_days=2)
        self.assertIn(dt.datetime.combine(tomorrow, dt.time(9, 0)), slots)
        self.assertNotIn(dt.datetime.combine(tomorrow, dt.time(10, 0)), slots)

    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_get_third_party_slots(self, _):
        # Third party callbacks should not care about capacity.
        tomorrow = dt.datetime.today() + dt.timedelta(days=1)
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=1, date=tomorrow, time="0900")
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=1, date=tomorrow, time="1000")

        slots = get_available_slots(num_days=2)
        self.assertIn(dt.datetime.combine(tomorrow, dt.time(9, 0)), slots)
        self.assertIn(dt.datetime.combine(tomorrow, dt.time(10, 0)), slots)

        # Book a callback for 10am tomorrow
        requires_action_at = dt.datetime.combine(tomorrow, dt.time(hour=10, minute=0))
        make_recipe(self.LEGALAID_CASE, requires_action_at=requires_action_at)

        slots = get_available_slots(num_days=2, is_third_party_callback=True)
        self.assertIn(dt.datetime.combine(tomorrow, dt.time(9, 0)), slots)
        self.assertIn(dt.datetime.combine(tomorrow, dt.time(10, 0)), slots)

    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_get_callback_slots_num_days(self, _):
        # This tests that slots are returned for the next n num_days.
        today_10_am = dt.datetime.combine(dt.datetime.today(), dt.time(10, 0))
        # Generate 31 days of datetimes
        days = [today_10_am + dt.timedelta(days=i) for i in range(1, 31)]

        for i in range(len(days)):
            slots = get_available_slots(num_days=i + 1)  # Plus 1 because we start checking from tomorrow.
            for day in days[:i]:
                assert day in slots
            for day in days[i + 1:]:
                assert day not in slots
