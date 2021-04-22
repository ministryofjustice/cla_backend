from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from core.tests.mommy_utils import make_recipe
from cla_eventlog.models import Log
from legalaid.models import Case


class FindAndDeleteOldCases(TestCase):
    def create_three_year_old_case(self):
        case = None
        freezer = freeze_time(timezone.now() + relativedelta(years=-3))
        freezer.start()
        case = make_recipe("legalaid.case")
        freezer.stop()
        return case

    def test_find_cases_viewed_two_years_ago(self):
        new_case = make_recipe("legalaid.case")
        old_case_1 = self.create_three_year_old_case()
        old_case_2 = self.create_three_year_old_case()

        self.assertEqual(len(Case.objects.all()), 3)

        make_recipe("cla_eventlog.log", case=new_case, code="CASE_VIEWED")
        make_recipe("cla_eventlog.log", case=old_case_1, code="CASE_VIEWED")
        make_recipe(
            "cla_eventlog.log", case=old_case_2, code="CASE_VIEWED", created=timezone.now() + relativedelta(years=-3)
        )

        self.assertEqual(len(Log.objects.all()), 3)

        logs_for_cases_created_two_years_old = Log.objects.filter(
            case__created__lte=timezone.now() + relativedelta(years=-2)
        )
        case_viewed_logs = logs_for_cases_created_two_years_old.filter(code__contains="CASE_VIEWED")
        cases_viewed_two_years_ago = case_viewed_logs.filter(created__lte=timezone.now() + relativedelta(years=-2))

        self.assertEqual(len(cases_viewed_two_years_ago), 1)
