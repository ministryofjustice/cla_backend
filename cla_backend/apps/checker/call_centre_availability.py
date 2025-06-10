from cla_common.constants import OPERATOR_HOURS, CALLBACK_TYPES
from cla_common.call_centre_availability import OpeningHours, current_datetime, SLOT_INTERVAL_MINS
from checker.models import CallbackTimeSlot
from checker.utils import get_timeslot_of_datetime
from django.utils import timezone
from legalaid.models import Case
import datetime


class CheckerOpeningHours(OpeningHours):
    def time_slots(self, callback_times, day=None, is_third_party_callback=False):
        """Gets all callback time slots on a given day.
        If is_third_party_callback = False capacity is ignored,
        otherwise the capacity will be based from the set of cases in range.

        Args:
            callback_times (List): List of callback date times
            day (datetime.date, optional): Date to get slots for. Defaults to None.
            is_third_party_callback (bool, optional): Is the callback for a third party. Defaults to False.

        Returns:
            slots: List of valid callback time slots.
        """
        slots = super(CheckerOpeningHours, self).time_slots(day)

        # cla_common gives all valid time slots from 00:00 to 23:30
        # The call centre doesn't work before 5AM, this allows us to check far fewer time slots and
        # also fix an ambiguous time error where 01:00:00 on a DST switchover date could belong to multiple
        # timezones.
        slots = filter(lambda dt: dt.hour > 5, slots)

        if is_third_party_callback:  # Third party callbacks always have capacity.
            return slots

        def has_capacity(slot):
            key = "%s %s" % (day.strftime(DATE_KEY_FORMAT), slot.strftime("%H%M"))
            if key not in capacity:
                return self.check_capacity_compared_to_prev_week(slot, callback_times)
            return capacity[key] > 0

        capacity = self.get_callback_with_capacity(day, callback_times)
        slots = filter(has_capacity, slots)
        return slots

    def get_callback_with_capacity(self, day, callback_times):
        callback_slots = CallbackTimeSlot.objects.filter(date=day).all()
        capacity = {}
        for callback_slot in callback_slots:
            key = "%s %s" % (day.strftime(DATE_KEY_FORMAT), callback_slot.time)
            used_capacity = count_callbacks_in_range(
                callback_times,
                callback_slot.callback_start_datetime(),
                callback_slot.callback_end_datetime() - datetime.timedelta(seconds=1),
            )
            capacity[key] = callback_slot.capacity - used_capacity
        return capacity

    def check_capacity_compared_to_prev_week(self, slot_dt, callback_times):
        """In the situation where no CallbackTimeSlot capacity has been defined for a given date
        the capacity of same timeslot for the previous week should be used.

        Args:
            slot_dt (datetime): Datetime of the slot which doesn't exist.

        Returns:
            Bool: If the slot would have capacity when compared to the capacity set by the previous week's slot.
        """
        slot_dt = timezone.make_aware(slot_dt)
        previous_timeslot = get_timeslot_of_datetime(slot_dt - datetime.timedelta(weeks=1))
        if not previous_timeslot:
            return True  # If there are no timeslots found for the previous year then fallback safely.

        num_slots_booked = count_callbacks_in_range(
            callback_times, slot_dt, slot_dt + datetime.timedelta(minutes=SLOT_INTERVAL_MINS)
        )

        # Compares the slots booked in the current week's timeslot to last weeks' capacity.
        return num_slots_booked < previous_timeslot.capacity


DATE_KEY_FORMAT = "%Y%m%d"
CALL_CENTER_HOURS = CheckerOpeningHours(**OPERATOR_HOURS)


def get_list_callback_times(start_dt, end_dt):
    """ Gets a list of requested callback times made via the web form within the given range.
        Excludes callbacks requested for a third party.

        Only includes cases with an outcome code of CB1, i.e. First callback attempt is yet to occur.

    Args:
        start_dt (datetime.datetime): Start of time range
        end_dt (datetime.datetime): End of time range

    Returns:
        list[datetime.datetime]: List of requested callback times.
    """
    callback_times = Case.objects.filter(
        requires_action_at__range=(start_dt, end_dt), callback_type=CALLBACK_TYPES.CHECKER_SELF, outcome_code="CB1"
    ).values_list("requires_action_at", flat=True)
    return callback_times


def count_callbacks_in_range(callback_times, start_dt, end_dt):
    """Returns the number of callbacks that are in the given range.

    Args:
        callback_times (list[datetime.datetime]): List of callback datetimes
        start_dt (datetime.datetime]): Start of the time range
        end_dt (datetime.datetime]): End of the time range

    Returns:
        Int: Num callbacks in the given range
    """
    times_in_range = list(
        filter(lambda callback_time: callback_time >= start_dt and callback_time < end_dt, callback_times)
    )
    return len(times_in_range)


def get_available_slots(num_days=7, is_third_party_callback=False):
    """Get a dictionary of available callback slots.

    Args:
        num_days (int, optional): _description_. Defaults to 7.
        is_third_party_callback (bool, optional): _description_. Defaults to False.

    Returns:
        Dict: Dictionary of callback slots in the form: {"YYYYMMDD":  {"HHMM": {"start": datetime, "end": datetime}}}
    """
    start_dt = current_datetime()
    days = [start_dt]
    # Generate time slots options for call on another day select options
    if num_days > 1:
        # available_days gives us all call centre working days meaning Sundays and bank holidays are excluded.
        days.extend(CALL_CENTER_HOURS.available_days(num_days - 1))  # days will always have length = num_days

    end_dt = datetime.datetime.combine(
        date=days[-1].date(), time=datetime.datetime.max.time()
    )  # 23:59:59 on the final date of relevant time period.

    # As making a Case query is expensive, we want to make a single query for relevant callback times and compare all time slots to this set of times.
    callback_times = get_list_callback_times(start_dt, end_dt)

    valid_slots = []
    for day in days:
        valid_slots.extend(CALL_CENTER_HOURS.time_slots(callback_times, day.date(), is_third_party_callback))

    return valid_slots
