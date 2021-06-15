from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from freezegun import freeze_time
import datetime

from core.tests.mommy_utils import make_recipe
from cla_eventlog.models import Log
from complaints.models import Complaint
from legalaid.models import Case, EODDetails, EligibilityCheck, PersonalDetails
from diagnosis.models import DiagnosisTraversal
from cla_auditlog.models import AuditLog
from cla_eventlog.management.commands.find_and_delete_old_cases import Command


def _make_datetime(year=None, month=None, day=None, hour=0, minute=0, second=0):
    today = datetime.date.today()
    year = year if year else today.year
    month = month if month else today.month
    day = day if day else today.day
    dt = datetime.datetime(year, month, day, hour, minute, second)
    return timezone.make_aware(dt, timezone.get_current_timezone())


class FindAndDeleteOldCases(TestCase):
    def setUp(self):
        super(FindAndDeleteOldCases, self).setUp()
        self.command = Command()

    def create_case(self, current_time, case_type="legalaid.case"):
        freezer = freeze_time(current_time)
        freezer.start()
        case = make_recipe(case_type)
        freezer.stop()
        return case

    def create_event_log_for_case(self, case, code, created, created_by=None):
        kwargs = {"case": case, "code": code, "created": created}
        if created_by:
            kwargs.update(created_by=created_by)
        make_recipe("cla_eventlog.log", **kwargs)

    def delete_old_cases(self, current_time):
        freezer = freeze_time(current_time)
        freezer.start()
        self.command.execute("delete")
        freezer.stop()

    def delete_logs(self, current_time):
        freezer = freeze_time(current_time)
        freezer.start()
        self.command.execute("delete-logs")
        freezer.stop()

    def find_old_cases(self, current_time):
        freezer = freeze_time(current_time)
        freezer.start()
        # Using handle method because command execute method can only return a string i.e it can't return a queryset
        cases = self.command.handle()
        freezer.stop()
        return cases

    def test_old_case_with_recent_event_logs_is_not_deleted(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date)

        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2014, month=5, day=30, hour=9))
        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2018, month=4, day=27, hour=9))
        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2020, month=4, day=27, hour=9))

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        oldCasesFound = self.find_old_cases(dt)
        self.assertEqual(oldCasesFound.count(), 0)

        self.delete_old_cases(dt)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(Log.objects.count(), 3)

    def test_old_case_with_recent_complaint_is_not_deleted(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date)

        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2014, month=5, day=30, hour=9))
        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2018, month=4, day=27, hour=9))

        complaint_date = _make_datetime(year=2020, month=4, day=27, hour=9)
        eod = make_recipe("legalaid.eod_details", case=case)
        log = make_recipe("cla_auditlog.audit_log")
        make_recipe("complaints.complaint", eod=eod, audit_log=[log], created=complaint_date)
        self.create_event_log_for_case(case, "COMPLAINT_CREATED", complaint_date)

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        oldCasesFound = self.find_old_cases(dt)
        self.assertEqual(oldCasesFound.count(), 0)

        self.delete_old_cases(dt)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(Complaint.objects.count(), 1)
        self.assertEqual(Log.objects.count(), 3)
        self.assertEqual(EODDetails.objects.count(), 1)

    def test_old_case_with_recent_means_test_change_is_not_deleted(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date, "legalaid.eligible_case")

        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2014, month=5, day=30, hour=9))
        self.create_event_log_for_case(case, "MT_CHANGED", _make_datetime(year=2020, month=4, day=27, hour=9))

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        oldCasesFound = self.find_old_cases(dt)
        self.assertEqual(oldCasesFound.count(), 0)

        self.delete_old_cases(dt)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(Log.objects.count(), 2)
        self.assertEqual(EligibilityCheck.objects.count(), 1)

    def test_old_case_with_two_logs_with_same_date_of_creation_is_not_deleted(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date, "legalaid.eligible_case")

        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2020, month=4, day=27, hour=9))
        self.create_event_log_for_case(case, "MT_CHANGED", _make_datetime(year=2020, month=4, day=27, hour=9))

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        oldCasesFound = self.find_old_cases(dt)
        self.assertEqual(oldCasesFound.count(), 0)

        self.delete_old_cases(dt)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(Log.objects.count(), 2)
        self.assertEqual(EligibilityCheck.objects.count(), 1)

    def test_relatively_new_case_with_no_event_logs_is_not_deleted(self):
        date = _make_datetime(year=2020, month=4, day=27, hour=9)
        self.create_case(date)

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        oldCasesFound = self.find_old_cases(dt)
        self.assertEqual(oldCasesFound.count(), 0)

        self.delete_old_cases(dt)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(Log.objects.count(), 0)

    def test_old_case_with_no_event_logs_is_deleted(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        self.create_case(date)

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        oldCasesFound = self.find_old_cases(dt)
        self.assertEqual(oldCasesFound.count(), 1)

        self.delete_old_cases(dt)
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(Log.objects.count(), 0)
        self.assertEqual(AuditLog.objects.count(), 0)
        self.assertEqual(Complaint.objects.count(), 0)
        self.assertEqual(EODDetails.objects.count(), 0)
        self.assertEqual(EligibilityCheck.objects.count(), 0)
        self.assertEqual(DiagnosisTraversal.objects.count(), 0)
        self.assertEqual(PersonalDetails.objects.count(), 0)

    def test_old_case_with_old_event_logs_is_deleted(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date)
        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2014, month=5, day=30, hour=9))
        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2018, month=4, day=27, hour=9))

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        oldCasesFound = self.find_old_cases(dt)
        self.assertEqual(oldCasesFound.count(), 1)

        self.delete_old_cases(dt)
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(Log.objects.count(), 0)
        self.assertEqual(AuditLog.objects.count(), 0)
        self.assertEqual(Complaint.objects.count(), 0)
        self.assertEqual(EODDetails.objects.count(), 0)
        self.assertEqual(EligibilityCheck.objects.count(), 0)
        self.assertEqual(DiagnosisTraversal.objects.count(), 0)
        self.assertEqual(PersonalDetails.objects.count(), 0)

    def test_old_case_with_old_means_test_changed_is_deleted(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date, "legalaid.eligible_case")
        self.create_event_log_for_case(case, "MT_CHANGED", _make_datetime(year=2014, month=5, day=30, hour=9))

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        oldCasesFound = self.find_old_cases(dt)
        self.assertEqual(oldCasesFound.count(), 1)

        self.delete_old_cases(dt)
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(Log.objects.count(), 0)
        self.assertEqual(AuditLog.objects.count(), 0)
        self.assertEqual(Complaint.objects.count(), 0)
        self.assertEqual(EODDetails.objects.count(), 0)
        self.assertEqual(EligibilityCheck.objects.count(), 0)
        self.assertEqual(DiagnosisTraversal.objects.count(), 0)
        self.assertEqual(PersonalDetails.objects.count(), 0)

    def test_old_and_new_cases_are_deleted_correctly(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case_0 = self.create_case(date, "legalaid.eligible_case")
        case_1 = self.create_case(date, "legalaid.eligible_case")
        case_2 = self.create_case(date, "legalaid.eligible_case")
        self.create_event_log_for_case(case_0, "MT_CHANGED", _make_datetime(year=2014, month=5, day=30, hour=9))
        self.create_event_log_for_case(case_0, "MT_CHANGED", _make_datetime(year=2018, month=5, day=30, hour=9))
        self.create_event_log_for_case(case_1, "MT_CHANGED", _make_datetime(year=2014, month=5, day=30, hour=9))
        self.create_event_log_for_case(case_2, "MT_CHANGED", _make_datetime(year=2020, month=4, day=27, hour=9))

        audit_log_1 = make_recipe("cla_auditlog.audit_log")
        audit_log_2 = make_recipe("cla_auditlog.audit_log")
        audit_log_3 = make_recipe("cla_auditlog.audit_log")
        eod_0 = make_recipe("legalaid.eod_details", case=case_0)
        eod_1 = make_recipe("legalaid.eod_details", case=case_1)
        eod_2 = make_recipe("legalaid.eod_details", case=case_2)
        make_recipe("complaints.complaint", eod=eod_0, audit_log=[audit_log_1])
        make_recipe("complaints.complaint", eod=eod_1, audit_log=[audit_log_2])
        make_recipe("complaints.complaint", eod=eod_2, audit_log=[audit_log_3])

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        with self.assertNumQueries(1):
            oldCasesFound = self.find_old_cases(dt)
            oldCasesFound.count()

        self.assertEqual(oldCasesFound.count(), 2)

        self.delete_old_cases(dt)
        case_ids = Case.objects.values_list("id", flat=True)
        # Check there is only 1 case and that case is the relatively new case
        self.assertEqual(list(case_ids), [case_2.id])
        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(AuditLog.objects.count(), 1)
        self.assertEqual(Complaint.objects.count(), 1)
        self.assertEqual(EODDetails.objects.count(), 1)
        self.assertEqual(EligibilityCheck.objects.count(), 1)
        self.assertEqual(DiagnosisTraversal.objects.count(), 1)
        self.assertEqual(PersonalDetails.objects.count(), 1)

    def test_case_viewed_by_digital_justice_user(self):
        case_date = _make_datetime(year=2014, month=5, day=24, hour=9)
        case = self.create_case(case_date, "legalaid.eligible_case")

        complaint_date = _make_datetime(year=2014, month=5, day=27, hour=9)
        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod, created=complaint_date)

        digital_justice_user = User.objects.create_user("digital_justice_user", "email@digital.justice.gov.uk")
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=5, day=27, hour=9), digital_justice_user
        )

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        self.delete_logs(dt)

        self.assertEqual(Log.objects.count(), 0)
        self.assertEqual(Case.objects.count(), 1)
        cases_with_digital_justice_user_logs = Case.objects.filter(log__created_by=digital_justice_user)
        self.assertEqual(cases_with_digital_justice_user_logs.count(), 0)

    def test_case_viewed_by_non_digital_justice_user(self):
        case_date = _make_datetime(year=2014, month=5, day=24, hour=9)
        case = self.create_case(case_date, "legalaid.eligible_case")

        complaint_date = _make_datetime(year=2014, month=5, day=27, hour=9)
        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod, created=complaint_date)

        non_digital_justice_user = User.objects.create_user("non_digital_justice_user", "chs.user@email.com")
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=6, day=27, hour=9), non_digital_justice_user
        )

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        self.delete_logs(dt)

        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        cases_with_digital_justice_user_logs = Case.objects.filter(log__created_by=non_digital_justice_user)
        self.assertEqual(cases_with_digital_justice_user_logs.count(), 1)

    def test_case_viewed_by_digital_and_non_digital_users(self):
        case_date = _make_datetime(year=2014, month=5, day=24, hour=9)
        case = self.create_case(case_date, "legalaid.eligible_case")

        complaint_date = _make_datetime(year=2014, month=5, day=27, hour=9)
        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod, created=complaint_date)

        digital_justice_user = User.objects.create_user("digital_justice_user", "email@digital.justice.gov.uk")
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=5, day=27, hour=9), digital_justice_user
        )

        non_digital_justice_user = User.objects.create_user("non_digital_justice_user", "chs.user@email.com")
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=6, day=27, hour=9), non_digital_justice_user
        )

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        self.delete_logs(dt)

        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)

        cases_with_digital_justice_user_logs = Case.objects.filter(log__created_by=digital_justice_user)
        # Implies implicitly that the non digital justice user log did not get deleted
        self.assertEqual(cases_with_digital_justice_user_logs.count(), 0)

    def test_case_viewed_same_day_by_digital_and_non_digital_users(self):
        case_date = _make_datetime(year=2014, month=5, day=24, hour=9)
        case = self.create_case(case_date, "legalaid.eligible_case")

        complaint_date = _make_datetime(year=2014, month=5, day=27, hour=9)
        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod, created=complaint_date)

        digital_justice_user = User.objects.create_user("digital_justice_user", "email@digital.justice.gov.uk")
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=5, day=27, hour=9), digital_justice_user
        )

        non_digital_justice_user = User.objects.create_user("non_digital_justice_user", "chs.user@email.com")
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=5, day=27, hour=9), non_digital_justice_user
        )

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        self.delete_logs(dt)

        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)

        cases_with_digital_justice_user_logs = Case.objects.filter(log__created_by=digital_justice_user)
        # Implies implicitly that the non digital justice user log did not get deleted
        self.assertEqual(cases_with_digital_justice_user_logs.count(), 0)

    def test_case_viewed_multiple_times_by_digital_and_non_digital_users(self):
        case_date = _make_datetime(year=2014, month=5, day=24, hour=9)
        case = self.create_case(case_date, "legalaid.eligible_case")

        complaint_date = _make_datetime(year=2014, month=5, day=27, hour=9)
        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod, created=complaint_date)

        digital_justice_user = User.objects.create_user("digital_justice_user", "email@digital.justice.gov.uk")
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=5, day=27, hour=9), digital_justice_user
        )
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=6, day=27, hour=9), digital_justice_user
        )
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=8, day=27, hour=9), digital_justice_user
        )

        non_digital_justice_user = User.objects.create_user("non_digital_justice_user", "chs.user@email.com")
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=3, day=22, hour=9), non_digital_justice_user
        )
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=6, day=22, hour=9), non_digital_justice_user
        )
        self.create_event_log_for_case(
            case, "CASE_VIEWED", _make_datetime(year=2020, month=9, day=21, hour=9), non_digital_justice_user
        )

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        self.delete_logs(dt)

        self.assertEqual(Log.objects.count(), 3)
        self.assertEqual(Case.objects.count(), 1)

        cases_with_digital_justice_user_logs = Case.objects.filter(log__created_by=digital_justice_user)
        # Implies implicitly that the non digital justice user logs did not get deleted
        self.assertEqual(cases_with_digital_justice_user_logs.count(), 0)

    def test_multiple_cases_viewed_by_multiple_users(self):
        case_1_date = _make_datetime(year=2014, month=5, day=24, hour=9)
        case_1 = self.create_case(case_1_date, "legalaid.eligible_case")

        case_2_date = _make_datetime(year=2014, month=9, day=29, hour=9)
        case_2 = self.create_case(case_2_date, "legalaid.eligible_case")

        complaint_1_date = _make_datetime(year=2014, month=5, day=27, hour=9)
        eod_1 = make_recipe("legalaid.eod_details", case=case_1)
        make_recipe("complaints.complaint", eod=eod_1, created=complaint_1_date)

        complaint_2_date = _make_datetime(year=2014, month=6, day=28, hour=9)
        eod_2 = make_recipe("legalaid.eod_details", case=case_2)
        make_recipe("complaints.complaint", eod=eod_2, created=complaint_2_date)

        digital_justice_user = User.objects.create_user("digital_justice_user", "email@digital.justice.gov.uk")
        self.create_event_log_for_case(
            case_1, "CASE_VIEWED", _make_datetime(year=2020, month=5, day=27, hour=9), digital_justice_user
        )
        self.create_event_log_for_case(
            case_2, "CASE_VIEWED", _make_datetime(year=2020, month=3, day=22, hour=9), digital_justice_user
        )

        non_digital_justice_user = User.objects.create_user("non_digital_justice_user", "chs.user@email.com")
        self.create_event_log_for_case(
            case_1, "CASE_VIEWED", _make_datetime(year=2020, month=5, day=30, hour=9), non_digital_justice_user
        )
        self.create_event_log_for_case(
            case_2, "CASE_VIEWED", _make_datetime(year=2020, month=3, day=30, hour=9), non_digital_justice_user
        )

        dt = _make_datetime(year=2021, month=1, day=1, hour=9)
        self.delete_logs(dt)

        self.assertEqual(Log.objects.count(), 2)
        self.assertEqual(Case.objects.count(), 2)

        cases_with_digital_justice_user_logs = Case.objects.filter(log__created_by=digital_justice_user)
        # Implies implicitly that the non digital justice user logs did not get deleted
        self.assertEqual(cases_with_digital_justice_user_logs.count(), 0)
