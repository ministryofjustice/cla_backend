from cla_common.constants import OPERATOR_HOURS, CALLBACK_TYPES
from cla_common.call_centre_availability import OpeningHours, current_datetime, SLOT_INTERVAL_MINS
from checker.models import CallbackTimeSlot
from checker.utils import get_timeslot_of_datetime
from legalaid.models import Case
import datetime


class CheckerOpeningHours(OpeningHours):
    def time_slots(self, cases_in_range, day=None, is_third_party_callback=False):
        """Gets all callback time slots on a given day.
        If is_third_party_callback = False capacity is ignored,
        otherwise the capacity will be based from the set of cases in range.

        Args:
            cases_in_range (QuerySet): Set of cases with callbacks
            day (datetime.date, optional): Date to get slots for. Defaults to None.
            is_third_party_callback (bool, optional): Is the callback for a third party. Defaults to False.

        Returns:
            slots: List of valid callback time slots.
        """
        slots = super(CheckerOpeningHours, self).time_slots(day)

        if is_third_party_callback:  # Third party callbacks always have capacity.
            return slots

        def has_capacity(slot):
            key = "%s %s" % (day.strftime(DATE_KEY_FORMAT), slot.strftime("%H%M"))
            if key not in capacity:
                return self.check_capacity_compared_to_prev_week(slot, cases_in_range)
            return capacity[key] > 0

        capacity = self.get_callback_with_capacity(day, cases_in_range)
        slots = filter(has_capacity, slots)
        return slots

    def get_callback_with_capacity(self, day, cases):
        callback_slots = CallbackTimeSlot.objects.filter(date=day).all()
        capacity = {}
        for callback_slot in callback_slots:
            key = "%s %s" % (day.strftime(DATE_KEY_FORMAT), callback_slot.time)
            used_capacity = cases.filter(
                requires_action_at__range=(
                    callback_slot.callback_start_datetime(),
                    callback_slot.callback_end_datetime() - datetime.timedelta(seconds=1),
                )
            ).count()
            capacity[key] = callback_slot.capacity - used_capacity
        return capacity

    def check_capacity_compared_to_prev_week(self, slot_dt, cases_in_range):
        """In the situation where no CallbackTimeSlot capacity has been defined for a given date
        the capacity of same timeslot for the previous week should be used.

        Args:
            slot_dt (datetime): Datetime of the slot which doesn't exist.

        Returns:
            Bool: If the slot would have capacity when compared to the capacity set by the previous week's slot.
        """
        previous_timeslot = get_timeslot_of_datetime(slot_dt - datetime.timedelta(weeks=1))
        if not previous_timeslot:
            return True  # If there are no timeslots found for the previous year then fallback safely.
        num_slots_booked = cases_in_range.filter(
            requires_action_at__range=(slot_dt, slot_dt + datetime.timedelta(minutes=SLOT_INTERVAL_MINS))
        ).count()

        # Compares the slots booked in the current week's timeslot to last weeks' capacity.
        return num_slots_booked < previous_timeslot.capacity


DATE_KEY_FORMAT = "%Y%m%d"
CALL_CENTER_HOURS = CheckerOpeningHours(**OPERATOR_HOURS)


def get_cases_with_callbacks_in_range(start_dt, end_dt):
    """Gets all cases which have a callback booked via the Checker web form, excluding third party callbacks.

    Args:
        start_dt (datetime.datetime): Start of time range
        end_dt (datetime.datetime): End of time range

    Returns:
        django.QuerySet: QuerySet of all relevant cases.
    """
    valid_cases = Case.objects.filter(
        requires_action_at__range=(start_dt, end_dt), callback_type=CALLBACK_TYPES.CHECKER_SELF
    ).all()
    return valid_cases


def get_available_slots(num_days=7, is_third_party_callback=False):
    """Get a dictionary of available callback slots.

    Args:
        num_days (int, optional): _description_. Defaults to 7.
        is_third_party_callback (bool, optional): _description_. Defaults to False.

    Returns:
        Dict: Dictionary of callback slots in the form: {"YYYYMMDD":  {"HHMM": {"start": datetime, "end": datetime}}}
    """
    start_dt = current_datetime()
    end_dt = start_dt + datetime.timedelta(days=7)
    days = [start_dt]
    # Generate time slots options for call on another day select options
    if num_days > 1:
        days.extend(CALL_CENTER_HOURS.available_days(num_days - 1))

    # As making a Case query is expensive, we want to make a single query for relevant cases and compare all time slots to this set of cases.
    cases_with_callbacks_in_range = get_cases_with_callbacks_in_range(start_dt, end_dt)

    valid_slots = []
    for day in days:
        valid_slots.extend(
            CALL_CENTER_HOURS.time_slots(cases_with_callbacks_in_range, day.date(), is_third_party_callback)
        )

    return valid_slots
