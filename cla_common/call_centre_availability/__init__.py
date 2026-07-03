import datetime

# need to replace ifilter as it cannot be called from python3 code
try:
    # Python 2
    from future_builtins import filter
except ImportError:
    # Python 3
    pass
from itertools import islice, takewhile
import pytz
import requests

from cla_common.services import CacheAdapter

BANK_HOLIDAYS_URL = "https://www.gov.uk/bank-holidays/england-and-wales.json"

SLOT_INTERVAL_MINS = 30

BOXING_DAY = datetime.date(year=2020, month=12, day=26)

TIMEZONE_NAME = None


def get_timezone():
    """
    Uses the timezone name to set up a pytz timezone instance
    Gets the timezone name from either Django settings or Flask conf.
    Does it within a function so that we don't try to access Django settings
    before they're ready.
    Stores it as a constant so that we're not calculating it every time
    """
    global TIMEZONE_NAME
    if not TIMEZONE_NAME:
        try:
            from django.conf import settings

            TIMEZONE_NAME = settings.TIME_ZONE
        except Exception as e:
            print(e)
            from flask import current_app

            TIMEZONE_NAME = current_app.config["TIMEZONE"]
    return pytz.timezone(TIMEZONE_NAME)


def current_datetime():
    # this function is to make unit testing simpler
    return datetime.datetime.now()


def in_the_past(time):
    return current_datetime() > time


def before_9am(time):
    return time.time() < datetime.time(9, 0)


def after_5pm(time):
    return time.time() >= datetime.time(17, 0)


def after_8pm(time):
    return time.time() >= datetime.time(20, 0)


def on_sunday(time):
    return time.weekday() == 6


def parse_date(text):
    return datetime.datetime.strptime(text, "%Y-%m-%d")


def get_date(bank_holiday):
    return parse_date(bank_holiday["date"])


class BankHolidays(object):
    def __init__(self):
        self._cache = None
        self.init_cache()

    def init_cache(self):
        self._cache = CacheAdapter.get_adapter()

    @property
    def url(self):
        return BANK_HOLIDAYS_URL

    @property
    def dates(self):
        dates = self._cached_dates

        if not dates:
            dates = self._parse_dates(self._load_dates())
            self._cached_dates = dates

        return dates

    @property
    def _cached_dates(self):
        if self._cache:
            return self._cache.get("bank_holidays")

    @_cached_dates.setter
    def _cached_dates(self, dates):
        if self._cache:
            one_year = 365 * 24 * 60 * 60
            self._cache.set("bank_holidays", dates, one_year)

    def _load_dates(self):
        return requests.get(self.url).json()["events"]

    def _parse_dates(self, events):
        return map(get_date, events)

    def __contains__(self, day):
        return day in self.dates


def bank_holidays():
    return BankHolidays()


def on_bank_holiday(time):
    day = datetime.datetime.combine(time.date(), datetime.time())
    return day in bank_holidays()


def is_boxing_day_2020(dt):
    return dt.date() == BOXING_DAY


def on_saturday(time):
    return time.weekday() == 5


def on_weekday(time):
    return time.weekday() < 5


def after_1230(time):
    return time.time() >= datetime.time(12, 30)


def is_today(time):
    return time.date() == current_datetime().date()


def too_late(time):
    start = current_datetime() + datetime.timedelta(hours=2)
    return time.time() < start.time()


def available(dt, ignore_time=False):
    if not (in_the_past(dt) or on_sunday(dt) or on_bank_holiday(dt) or is_boxing_day_2020(dt)):
        return ignore_time or not ((before_9am(dt) or after_8pm(dt)) or (on_saturday(dt) and after_1230(dt)))
    return False


def can_schedule_callback(dt):
    if is_today(dt) and too_late(dt):
        return False
    return available(dt)


def every_interval(time, days=0, hours=0, minutes=0):
    interval = datetime.timedelta(days=days, hours=hours, minutes=minutes)
    while True:
        yield time
        time += interval


def available_days(num):
    days = every_interval(current_datetime(), days=1)
    available_day = lambda day: available(day, ignore_time=True)
    return list(islice(filter(available_day, days), num))


def time_slots(day=None):
    if not day:
        day = datetime.date(9999, 1, 1)  # a weekday in the future
    start = datetime.datetime.combine(day, datetime.time(9))
    same_day = lambda x: x.date() == day
    slots = takewhile(same_day, every_interval(start, minutes=SLOT_INTERVAL_MINS))
    is_available = lambda slot: can_schedule_callback(slot)
    return list(filter(is_available, slots))


def today_slots(*args):
    return time_slots(current_datetime().date())


def tomorrow_slots(*args):
    tomorrow = current_datetime() + datetime.timedelta(days=1)
    return time_slots(tomorrow.date())


class Hours(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def is_empty(self):
        return not (self.start and self.end)

    def __nonzero__(self):
        # py2 support
        return self.__bool__()

    def __bool__(self):
        return not self.is_empty()

    def __contains__(self, dt):
        return self.contains(dt)

    def contains(self, dt, tz_aware=False):
        if self.is_empty():
            return False
        if tz_aware:
            tz_start = get_timezone().localize(dt.combine(dt, self.start))
            tz_end = get_timezone().localize(dt.combine(dt, self.end))
            return tz_start <= dt < tz_end
        else:
            return self.start <= dt.time() < self.end

    def __repr__(self):
        if self.is_empty():
            return "No hours"
        return "{start} - {end}".format(start=self.start, end=self.end)


NO_HOURS = Hours(None, None)


def make_date_matcher(date_string):
    def date_matcher(dt):
        date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
        return dt.date() == date

    return date_matcher


def make_day_matcher(day):
    def day_matcher(dt):
        return dt.strftime("%A") == day

    return day_matcher


class OpeningHours(object):
    def __init__(
        self,
        monday=None,
        tuesday=None,
        wednesday=None,
        thursday=None,
        friday=None,
        weekday=NO_HOURS,
        saturday=NO_HOURS,
        sunday=NO_HOURS,
        bank_holiday=NO_HOURS,
        **kwargs
    ):
        self.day_hours = []
        # want to use this library in python2 and python3
        # need to use items() (replacement for iteritems() in python3) but is slow in python 2
        for date_string, hours in kwargs.items():
            self.add_rule(make_date_matcher(date_string), hours)

        self.add_rule(on_bank_holiday, bank_holiday)

        for day, hours in [
            ("Monday", monday),
            ("Tuesday", tuesday),
            ("Wednesday", wednesday),
            ("Thursday", thursday),
            ("Friday", friday),
            ("Saturday", saturday),
            ("Sunday", sunday),
        ]:
            self.add_rule(make_day_matcher(day), hours)

        self.add_rule(on_weekday, weekday)

    def __contains__(self, dt):
        return self.available(dt)

    def add_rule(self, func, hours):
        if hours is None:
            return
        if hours and not isinstance(hours, Hours):
            hours = Hours(*hours)
        self.day_hours.append((func, hours))

    def available(self, dt, ignore_time=False, tz_aware=False):
        for (on_day, hours) in self.day_hours:
            if on_day(dt):
                if hours is None:
                    continue
                if hours and ignore_time:
                    return True
                return hours.contains(dt, tz_aware=tz_aware)
        return False

    def can_schedule_callback(self, dt, ignore_time=False):
        if in_the_past(dt):
            return False
        if is_today(dt) and too_late(dt):
            return False
        return self.available(dt, ignore_time=ignore_time)

    def time_slots(self, day=None):
        if not day:
            day = datetime.date(9999, 1, 1)  # a weekday in the future
        start = datetime.datetime.combine(day, datetime.time(0))
        same_day = lambda dt: dt.date() == day
        available = lambda dt: self.can_schedule_callback(dt)
        return list(filter(available, takewhile(same_day, every_interval(start, minutes=SLOT_INTERVAL_MINS))))

    def today_slots(self):
        return self.time_slots(current_datetime().date())

    def tomorrow_slots(self):
        tomorrow = current_datetime() + datetime.timedelta(days=1)
        return self.time_slots(tomorrow.date())

    def available_days(self, num_days=6):
        start = current_datetime() + datetime.timedelta(days=1)
        days = every_interval(start, days=1)
        available_day = lambda day: self.can_schedule_callback(day, ignore_time=True)
        return list(islice(filter(available_day, days), num_days))
