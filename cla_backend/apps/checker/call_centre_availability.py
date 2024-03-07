import datetime
from collections import OrderedDict
from cla_common.constants import OPERATOR_HOURS
from cla_common.call_centre_availability import SLOT_INTERVAL_MINS, OpeningHours
from checker.models import CallbackTimeSlot


CALL_CENTER_HOURS = OpeningHours(**OPERATOR_HOURS)


def get_available_slots(num_days=6):

    """Generate time slots options for call on another day select options"""
    days = CALL_CENTER_HOURS.available_days(num_days)
    slots = dict(map(time_slots, days))
    return slots


def time_choice(time):
    end = time + datetime.timedelta(minutes=SLOT_INTERVAL_MINS)
    display_string = format_time(time) + " - " + format_time(end)
    return time.strftime("%H%M"), display_string


def format_time(dt):
    if isinstance(dt, datetime.datetime):
        time = dt.time()
    else:
        time = dt
    display_format = "%H:%M"
    display_string = time.strftime(display_format)
    return display_string


def time_slots_for_day(day):
    callback_slots = CallbackTimeSlot.objects.filter(date=day).all()
    capacity = {}
    for callback_slot in callback_slots:
        key = "%s %s" % (day.strftime("%Y%m%d"), callback_slot.time)
        capacity[key] = callback_slot.remaining_capacity

    slots = CALL_CENTER_HOURS.time_slots(day)
    slots = filter(CALL_CENTER_HOURS.can_schedule_callback, slots)

    def has_capacity(slot):
        key = "%s %s" % (day.strftime("%Y%m%d"), slot.strftime("%H%M"))
        if key not in capacity:
            return True
        return capacity[key] > 0

    slots = filter(has_capacity, slots)
    return map(time_choice, slots)


def time_slots(day):
    slots = OrderedDict(time_slots_for_day(day.date()))
    return (format_day(day), slots)


def format_day(value):
    if isinstance(value, (datetime.date, datetime.datetime)):
        return "{:%Y%m%d}".format(value)
    return value
