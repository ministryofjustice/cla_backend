from cla_common.constants import OPERATOR_HOURS
from cla_common.call_centre_availability import OpeningHours, current_datetime
from checker.models import CallbackTimeSlot


class CheckerOpeningHours(OpeningHours):
    def time_slots(self, day=None, is_third_party_callback=False):
        slots = super(CheckerOpeningHours, self).time_slots(day)

        if is_third_party_callback:  # Third party callbacks always have capacity.
            return slots

        def has_capacity(slot):
            key = "%s %s" % (day.strftime(DATE_KEY_FORMAT), slot.strftime("%H%M"))
            if key not in capacity:
                return True
            return capacity[key] > 0

        capacity = self.get_callback_with_capacity(day)
        slots = filter(has_capacity, slots)
        return slots

    def get_callback_with_capacity(self, day):
        callback_slots = CallbackTimeSlot.objects.filter(date=day).all()
        capacity = {}
        for callback_slot in callback_slots:
            key = "%s %s" % (day.strftime(DATE_KEY_FORMAT), callback_slot.time)
            capacity[key] = callback_slot.remaining_capacity
        return capacity


DATE_KEY_FORMAT = "%Y%m%d"
CALL_CENTER_HOURS = CheckerOpeningHours(**OPERATOR_HOURS)


def get_available_slots(num_days=7, is_third_party_callback=False):
    """Get a dictionary of available callback slots.

    Args:
        num_days (int, optional): _description_. Defaults to 7.
        is_third_party_callback (bool, optional): _description_. Defaults to False.

    Returns:
        Dict: Dictionary of callback slots in the form: {"YYYYMMDD":  {"HHMM": {"start": datetime, "end": datetime}}}
    """

    days = [current_datetime()]
    # Generate time slots options for call on another day select options
    if num_days > 1:
        days.extend(CALL_CENTER_HOURS.available_days(num_days - 1))

    valid_slots = []
    for day in days:
        valid_slots.extend(CALL_CENTER_HOURS.time_slots(day.date(), is_third_party_callback))
    return valid_slots
