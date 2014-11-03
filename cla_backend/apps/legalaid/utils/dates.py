import datetime

from django.utils import timezone


def is_bank_holiday(dt):
    # TODO: make this work for bank hols
    return False


def is_out_of_hours(
    dt,
    weekday_time_start, weekday_time_end,
    sat_time_start, sat_time_end
):
    """
        Returns True is dt is out of hours, False otherwise

        dt: datetime in localtime (NOT UTC)
        weekday_time_start: start datetime.time during weekdays
        weekday_time_end: end datetime.time during weekdays
        sat_time_start: start datetime.time on Saturdays
        sat_time_end: end datetime.time during Saturdays
    """
    def dt_at(dt, hour, minute=0, second=0, microsecond=0):
        t = timezone.localtime(dt)
        return t.replace(hour=hour, minute=minute, second=second,
                         microsecond=microsecond)

    weekday = dt.weekday()

    # not open on bank holiday
    if is_bank_holiday(dt):
        return True

    # if day in MON-FRI (open 09h-17h)
    elif weekday < 5:
        day_start = dt_at(dt, hour=weekday_time_start.hour, minute=weekday_time_start.minute)
        day_end = dt_at(dt, hour=weekday_time_end.hour, minute=weekday_time_end.minute)
        return not (day_start < dt < day_end)

    # if Saturday (only open in the morning)
    elif ((sat_time_start and sat_time_end) and weekday == 5):
        day_start = dt_at(dt, hour=sat_time_start.hour, minute=sat_time_start.minute)
        day_end = dt_at(dt, hour=sat_time_end.hour, minute=sat_time_end.minute)
        return not (day_start < dt < day_end)

    # if Sunday then out of hours (call centre doesn't operate on sunday)
    else:
        return True


def is_out_of_hours_for_providers(dt):
    """
        Returns True is dt is out of hours for specialists,
            False otherwise

        Currently working hours for specialists run:
            Mon-Fri: 9am - 5pm

        dt: datetime in localtime (NOT UTC)
    """
    return is_out_of_hours(
        dt=dt,
        weekday_time_start=datetime.time(hour=9, minute=0),
        weekday_time_end=datetime.time(hour=17, minute=0),
        sat_time_start=None,
        sat_time_end=None
    )


def is_out_of_hours_for_operators(dt):
    """
        Returns True is dt is out of hours for operators,
            False otherwise

        Currently working hours for operators run:
            Mon-Fri: 9am - 8pm
            Sat: 9am - 12.30pm

        dt: datetime in localtime (NOT UTC)
    """
    return is_out_of_hours(
        dt=dt,
        weekday_time_start=datetime.time(hour=9, minute=0),
        weekday_time_end=datetime.time(hour=20, minute=0),
        sat_time_start=datetime.time(hour=9, minute=0),
        sat_time_end=datetime.time(hour=12, minute=30)
    )
