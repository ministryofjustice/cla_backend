from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import datetime

from core.tests.mommy_utils import make_recipe
from cla_eventlog.models import Log
from legalaid.models import Case


def _make_datetime(year=None, month=None, day=None, hour=0, minute=0, second=0):
    today = datetime.date.today()
    year = year if year else today.year
    month = month if month else today.month
    day = day if day else today.day
    dt = datetime.datetime(year, month, day, hour, minute, second)
    return timezone.make_aware(dt, timezone.get_current_timezone())


class FindAndDeleteOldCases(TestCase):
    def create_case(self, created_at):
        case = None
        freezer = freeze_time(created_at)
        freezer.start()
        case = make_recipe("legalaid.case")
        freezer.stop()
        return case

    def create_event_log_for_case(self, case, code, created):
        make_recipe("cla_eventlog.log", case=case, code=code, created=created)

    def test_old_case_with_recent_event_logs(self):
        date = datetime.datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date)

        self.create_event_log_for_case(case, "CASE_VIEWED", datetime.datetime(year=2014, month=5, day=30, hour=9))
        self.create_event_log_for_case(case, "CASE_VIEWED", datetime.datetime(year=2018, month=4, day=27, hour=9))
        self.create_event_log_for_case(case, "CASE_VIEWED", datetime.datetime(year=2020, month=4, day=27, hour=9))

        self.delete_old_cases(_make_datetime(year=2021, month=1, day=1, hour=9))

        cases = Case.objects.all()
        self.assertEqual(len(cases), 1)

    def delete_old_cases(self, date):
        two_years_ago = date + relativedelta(years=-2)

        event_log_cases = self.get_old_cases(two_years_ago)
        for case in event_log_cases:
            case.delete()

    def get_old_cases(self, date):
        old_cases = []
        filtered_cases = Case.objects.filter(created__lte=date)

        for case in filtered_cases:
            try:
                latest_log = Log.objects.filter(case__id=case.id).latest("created")
                if latest_log.created <= date:
                    old_cases.append(case)
            except Log.DoesNotExist:
                # Delete old case without any event logs
                old_cases.append(case)

        return old_cases
