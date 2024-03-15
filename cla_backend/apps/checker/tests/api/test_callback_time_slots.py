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
    RESOURCE_RECIPE = "checker.callback_time_slot"

    def setup_resources(self):
        pass

    # Make sure all times are available
    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_slots(self, mock_opening_hours_available):
        # Create callback time slots with capacity
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        make_recipe("checker.callback_time_slot", capacity=2, date=tomorrow, time="0900")
        make_recipe("checker.callback_time_slot", capacity=1, date=tomorrow, time="1000")
        # This callback has no capacity so it should not be bookable
        make_recipe("checker.callback_time_slot", capacity=0, date=tomorrow, time="1100")
        slots = get_available_slots(num_days=2)
        slot = slots[tomorrow.strftime(DATE_KEY_FORMAT)]
        self.assertTrue("0900" in slot)
        self.assertTrue("1000" in slot)
        self.assertFalse("1100" in slot)

        # Book a callback for 10am tomorrow. 10am slot only has a capacity of 1, after this it should not be available
        requires_action_at = datetime.datetime.combine(tomorrow, datetime.time(hour=10, minute=0))
        make_recipe("legalaid.case", requires_action_at=requires_action_at)
        slots = get_available_slots(num_days=2)
        slot = slots[tomorrow.strftime(DATE_KEY_FORMAT)]
        self.assertTrue("0900" in slot)
        self.assertFalse("1000" in slot)
        self.assertFalse("1100" in slot)
