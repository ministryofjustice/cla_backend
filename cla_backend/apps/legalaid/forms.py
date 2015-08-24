from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from cla_common.call_centre_availability import SLOT_INTERVAL_MINS, \
    OpeningHours, available_days, time_slots
from cla_eventlog.forms import BaseCaseLogForm


def is_in_business_hours(dt):
    if not dt.tzinfo:
        dt = timezone.make_aware(dt, timezone.get_default_timezone())

    OPERATOR_HOURS = OpeningHours(**settings.OPERATOR_HOURS)
    return dt in OPERATOR_HOURS


def get_remainder_from_end_of_day(day, dt_until):
    available_slots = time_slots(day)
    remainder = timedelta(minutes=SLOT_INTERVAL_MINS)
    if available_slots:
        end_of_day = available_slots[-1] + timedelta(minutes=SLOT_INTERVAL_MINS)
        end_of_day = timezone.make_aware(end_of_day, timezone.get_default_timezone())
        remainder = dt_until - end_of_day
    assert remainder >= timedelta(microseconds=0)
    return remainder


def get_next_business_day(start_date):
    return filter(lambda x: x.date() > start_date, available_days(365))[0]


def get_sla_time(start_time, minutes):
    next_business_day = get_next_business_day(start_time.date())
    start_of_next_business_day = time_slots(next_business_day.date())[0]
    start_of_next_business_day = timezone.make_aware(start_of_next_business_day,
        timezone.get_default_timezone())

    if not is_in_business_hours(start_time):
        start_time = start_of_next_business_day

    simple_delta = start_time + timedelta(minutes=minutes)
    in_business_hours = is_in_business_hours(simple_delta)
    if not in_business_hours:
        remainder_delta = get_remainder_from_end_of_day(start_time.date(), simple_delta)
        return get_sla_time(start_of_next_business_day, remainder_delta.total_seconds() // 60 )
    return simple_delta


class BaseCallMeBackForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'call_me_back'

    def get_requires_action_at(self):
        raise NotImplementedError()

    def get_context(self):
        requires_action_at = self.get_requires_action_at()

        _dt = timezone.localtime(requires_action_at)
        return {
            'requires_action_at': _dt,
            'sla_15': get_sla_time(_dt, 15),
            'sla_30': get_sla_time(_dt, 30),
            'sla_120': get_sla_time(_dt, 120),
            'sla_480': get_sla_time(_dt, 480)
        }

    def get_notes(self):
        dt = timezone.localtime(self.get_requires_action_at())
        return u"Callback scheduled for {dt}. {notes}".format(
            dt=dt.strftime("%d/%m/%Y %H:%M"),
            notes=self.cleaned_data['notes'] or ""
        )

    def save(self, user):
        super(BaseCallMeBackForm, self).save(user)
        dt = self.get_requires_action_at()
        self.case.set_requires_action_at(dt)
