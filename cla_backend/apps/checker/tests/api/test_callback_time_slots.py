import mock
import datetime
from rest_framework.test import APITestCase
from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin
from legalaid.tests.views.test_base import CLACheckerAuthBaseApiTestMixin
from checker.call_centre_availability import get_available_slots, DATE_KEY_FORMAT


class CallbackTimeSlotsTestCase(SimpleResourceAPIMixin, CLACheckerAuthBaseApiTestMixin, APITestCase):
    LOOKUP_KEY = "id"
    API_URL_BASE_NAME = "callback_time_slots"
    CALLBACK_TIME_SLOT = "checker.callback_time_slot"

    def setup_resources(self):
        pass

    # Make sure all times are available
    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_slots(self, _):
        # Create callback time slots with capacity
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=2, date=tomorrow, time="0900")
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=1, date=tomorrow, time="1000")
        # This callback has no capacity so it should not be bookable
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=0, date=tomorrow, time="1100")
        slots = get_available_slots(num_days=2)
        slot = slots[tomorrow.strftime(DATE_KEY_FORMAT)]
        self.assertIn("0900", slot)
        self.assertIn("1000", slot)
        self.assertNotIn("1100", slot)

        # Book a callback for 10am tomorrow. 10am slot only has a capacity of 1, after this it should not be available
        requires_action_at = datetime.datetime.combine(tomorrow, datetime.time(hour=10, minute=0))
        make_recipe("legalaid.case", requires_action_at=requires_action_at)
        slots = get_available_slots(num_days=2)
        slot = slots[tomorrow.strftime(DATE_KEY_FORMAT)]
        self.assertIn("0900", slot)
        self.assertNotIn("1000", slot)

    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_negative_capacity(self, _):
        # This handles the case where an operator overrides the capacity rules and the capacity becomes negative.
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=1, date=tomorrow, time="0900")
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=1, date=tomorrow, time="1000")

        slots = get_available_slots(num_days=2)
        slot = slots[tomorrow.strftime(DATE_KEY_FORMAT)]
        self.assertIn("0900", slot)
        self.assertIn("1000", slot)

        # Book two callbacks for 10am tomorrow, this should make the capacity negative
        requires_action_at = datetime.datetime.combine(tomorrow, datetime.time(hour=10, minute=0))
        for _ in range(2):
            make_recipe("legalaid.case", requires_action_at=requires_action_at)
        slots = get_available_slots(num_days=2)
        slot = slots[tomorrow.strftime(DATE_KEY_FORMAT)]
        self.assertIn("0900", slot)
        self.assertNotIn("1000", slot)

    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_get_third_party_slots(self, _):
        # Third part callbacks should not care about capacity.
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=1, date=tomorrow, time="0900")
        make_recipe(self.CALLBACK_TIME_SLOT, capacity=1, date=tomorrow, time="1000")

        slots = get_available_slots(num_days=2)
        slot = slots[tomorrow.strftime(DATE_KEY_FORMAT)]
        self.assertIn("0900", slot)
        self.assertIn("1000", slot)

        # Book a callback for 10am tomorrow
        requires_action_at = datetime.datetime.combine(tomorrow, datetime.time(hour=10, minute=0))
        make_recipe("legalaid.case", requires_action_at=requires_action_at)

        slots = get_available_slots(num_days=2, is_third_party_callback=True)
        slot = slots[tomorrow.strftime(DATE_KEY_FORMAT)]
        self.assertIn("0900", slot)
        self.assertIn("1000", slot)

    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_get_callback_slots_num_days(self, _):
        # Generate 31 days of datetimes
        today = datetime.datetime.today()
        days = [today + datetime.timedelta(days=i) for i in range(31)]

        # Turn the datetimes into the string format returned from get_available_slots
        days = list(map(lambda day: day.strftime(DATE_KEY_FORMAT) if day.date() != today.date() else 'today', days))

        for i in range(len(days)):
            # Iterate across the week and assert that the days start appearing as expected
            slots = get_available_slots(num_days=i)
            for day in days[:i]:
                assert day in slots.keys()
            for day in days[i + 1:]:
                assert day not in slots.keys()
