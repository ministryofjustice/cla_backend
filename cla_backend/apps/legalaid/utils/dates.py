import datetime

from django.utils import timezone

from cla_common.call_centre_availability import on_bank_holiday, on_sunday, \
    on_saturday


class OpeningHours(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __contains__(self, dt):
        return self.start < dt.time() < self.end


def is_out_of_hours(dt, weekday_hours, saturday_hours):
    """
        Returns True if dt is out of hours, False otherwise

        dt: datetime in localtime (NOT UTC)
        weekday_hours: OpeningHours during weekdays
        saturday_hours: OpeningHours on Saturdays
    """

    if on_bank_holiday(dt):
        return True

    if on_sunday(dt):
        return True

    if on_saturday(dt) and dt not in saturday_hours:
        return True

    if dt not in weekday_hours:
        return True

    return False


def is_out_of_hours_for_providers(dt):
    """
        Returns True if dt is out of hours for specialists,
            False otherwise

        Currently working hours for specialists run:
            Mon-Fri: 9am - 5pm
            Sat: 9am - 12.30pm

        dt: datetime in localtime (NOT UTC)
    """
    mon_fri = OpeningHours(datetime.time(9, 0), datetime.time(17, 0))
    sat = OpeningHours(datetime.time(9, 0), datetime.time(12, 30))
    return is_out_of_hours(dt, mon_fri, sat)


def is_out_of_hours_for_operators(dt):
    """
        Returns True if dt is out of hours for operators,
            False otherwise

        Currently working hours for operators run:
            Mon-Fri: 9am - 8pm
            Sat: 9am - 12.30pm

        dt: datetime in localtime (NOT UTC)
    """
    mon_fri = OpeningHours(datetime.time(9, 0), datetime.time(20, 0))
    sat = OpeningHours(datetime.time(9, 0), datetime.time(12, 30))
    return is_out_of_hours(dt, mon_fri, sat)
