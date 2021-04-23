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

    def create_event_log_for_case(self, case, code, created=None):
        if created:
            make_recipe("cla_eventlog.log", case=case, code=code, created=created)
        else:
            make_recipe("cla_eventlog.log", case=case, code=code)

    def test_find_cases_viewed_two_years_ago(self):
        new_case = make_recipe("legalaid.case")
        old_case_1 = self.create_three_year_old_case()
        old_case_2 = self.create_three_year_old_case()

        self.assertEqual(len(Case.objects.all()), 3)

        self.create_event_log_for_case(new_case, "CASE_VIEWED")
        self.create_event_log_for_case(new_case, "CASE_CREATED")
        self.create_event_log_for_case(new_case, "CASE_VIEWED", created=timezone.now() + relativedelta(years=-3))

        self.create_event_log_for_case(old_case_1, "CASE_VIEWED")
        self.create_event_log_for_case(old_case_1, "MT_CHANGED")
        self.create_event_log_for_case(old_case_1, "CASE_VIEWED", created=timezone.now() + relativedelta(years=-1))

        self.create_event_log_for_case(old_case_2, "CASE_VIEWED", created=timezone.now() + relativedelta(years=-3))
        self.create_event_log_for_case(old_case_2, "CASE_CREATED", created=timezone.now() + relativedelta(years=-3))
        self.create_event_log_for_case(old_case_2, "CASE_VIEWED", created=timezone.now() + relativedelta(years=-2))

        logs = Log.objects.all()

        self.assertEqual(len(logs), 9)

        event_logs_created_two_years_ago = Log.objects.filter(
            # Cases created two years ago or over
            case__created__lte=timezone.now() + relativedelta(years=-2),
            # That have logs created two years ago or over
            created__lte=timezone.now() + relativedelta(years=-2),
            # Where the code field on the log = "CASE_VIEWED"
            code__contains="CASE_VIEWED",
        )
        self.assertEqual(len(event_logs_created_two_years_ago), 2)
        for log in event_logs_created_two_years_ago:
            self.assertIn(log.case.id, [old_case_2.id])
