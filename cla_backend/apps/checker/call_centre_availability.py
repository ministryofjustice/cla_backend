import datetime
from collections import OrderedDict
from cla_common.constants import OPERATOR_HOURS
from cla_common.call_centre_availability import SLOT_INTERVAL_MINS, OpeningHours, current_datetime
from checker.models import CallbackTimeSlot


class CheckerOpeningHours(OpeningHours):
    def time_slots(self, day=None, is_third_party_callback=False):
        capacity = self.get_callback_with_capacity(day)
        slots = super(CheckerOpeningHours, self).time_slots(day)

        def has_capacity(slot):
            key = "%s %s" % (day.strftime(DATE_KEY_FORMAT), slot.strftime("%H%M"))
            if key not in capacity:
                # TODO: Add rules re taking last weeks capacity here.
                return True
            return capacity[key] > 0

        if is_third_party_callback:  # Third party callbacks always have capacity.
            return slots

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

    # Generate time slots options for call on another day select options
    days = CALL_CENTER_HOURS.available_days(num_days - 1) if num_days > 1 else []
    # Add today to list of available days
    days.insert(0, current_datetime())
    slots = map(lambda day: time_slots(day, is_third_party_callback), days)
    return dict(slots)


def time_choice(time):
    end = time + datetime.timedelta(minutes=SLOT_INTERVAL_MINS)
    return time.strftime("%H%M"), {"start": time, "end": end}


def format_time(dt):
    if isinstance(dt, datetime.datetime):
        time = dt.time()
    else:
        time = dt
    display_format = "%H:%M"
    display_string = time.strftime(display_format)
    return display_string


def time_slots_for_day(day, is_third_party_callback=False):
    slots = CALL_CENTER_HOURS.time_slots(day, is_third_party_callback)
    slots = filter(CALL_CENTER_HOURS.can_schedule_callback, slots)
    return map(time_choice, slots)


def time_slots(day, is_third_party_callback=False):
    slots = OrderedDict(time_slots_for_day(day.date(), is_third_party_callback))
    return (format_day(day), slots)


def format_day(value):
    if isinstance(value, (datetime.date, datetime.datetime)):
        value = value.date() if isinstance(value, datetime.datetime) else value
        if value == datetime.date.today():
            return "today"
        return "{:%Y%m%d}".format(value)
    return value
