# -*- coding: utf-8 -*-
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

from cla_common.call_centre_availability import SLOT_INTERVAL_MINS, OpeningHours, \
    available_days, on_sunday, on_bank_holiday


operator_hours = OpeningHours(**settings.OPERATOR_HOURS)


def is_in_business_hours(dt):
    if not dt.tzinfo:
        dt = timezone.make_aware(dt, timezone.get_default_timezone())
    return dt in operator_hours


def get_remainder_from_end_of_day(day, dt_until):
    available_slots = operator_hours.time_slots(day)
    remainder = timedelta(minutes=SLOT_INTERVAL_MINS)
    if available_slots:
        end_of_day = available_slots[-1] + timedelta(minutes=SLOT_INTERVAL_MINS)
        end_of_day = timezone.make_aware(end_of_day, timezone.get_default_timezone())
        remainder = dt_until - end_of_day
    assert remainder >= timedelta(microseconds=0)
    return remainder


def get_next_business_day(start_date):
    return filter(lambda x: x.date() > start_date, available_days(365))[0]


def get_sla_time(start_time, minutes_delta):
    next_business_day = get_next_business_day(start_time.date())
    start_of_next_business_day = operator_hours.time_slots(next_business_day.date())[0]
    start_of_next_business_day = timezone.make_aware(start_of_next_business_day,
        timezone.get_default_timezone())

    if not is_in_business_hours(start_time):
        start_time = start_of_next_business_day

    simple_delta = start_time + timedelta(minutes=minutes_delta)
    in_business_hours = is_in_business_hours(simple_delta)
    if not in_business_hours:
        remainder_delta = get_remainder_from_end_of_day(start_time.date(), simple_delta)
        return get_sla_time(start_of_next_business_day, remainder_delta.total_seconds() // 60 )
    return simple_delta


def get_day_sla_time(start_time, days):
    sla_time = start_time
    work_days = 0
    while work_days < days:
        sla_time += timedelta(days=1)
        if not on_sunday(sla_time) and not on_bank_holiday(sla_time):
            work_days += 1
    return sla_time
