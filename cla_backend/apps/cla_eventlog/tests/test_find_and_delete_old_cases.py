from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from cla_butler.tasks import get_pks
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

        case_pks = get_pks(Case.objects.all())
        cases_and_logs = {}

        for case_pk in case_pks:
            case = Case.objects.get(id=case_pk)
            # Logs are arranged in descending order based upon the event_logs Meta ordering setting
            case_logs = Log.objects.filter(case__id=case_pk, code="CASE_VIEWED")
            cases_and_logs[case.reference] = case_logs

        cases_to_delete = []
        two_years_ago = timezone.now() + relativedelta(years=-2)

        for case_reference, case_logs in cases_and_logs.items():
            latest_log = case_logs.first()
            if latest_log.created <= two_years_ago:
                cases_to_delete.append(case_reference)

        self.assertEqual(len(cases_to_delete), 1)

        for case_reference, case_logs in cases_and_logs.items():
            case_id = Case.objects.get(reference=case_reference).id
            for log in case_logs:
                self.assertIn(log.case.id, [case_id])
