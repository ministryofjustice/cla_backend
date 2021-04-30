from django.test import TestCase
from django.utils import timezone
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
    def create_case(self, current_time, case_type="legalaid.case"):
        case = None
        freezer = freeze_time(current_time)
        freezer.start()
        case = make_recipe(case_type)
        freezer.stop()
        return case

    def create_event_log_for_case(self, case, code, created):
        make_recipe("cla_eventlog.log", case=case, code=code, created=created)

    def delete_old_cases(self, current_time):
        freezer = freeze_time(current_time)
        freezer.start()
        Command().execute()
        freezer.stop()

    def test_old_case_with_recent_event_logs(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date)

        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2014, month=5, day=30, hour=9))
        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2018, month=4, day=27, hour=9))
        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2020, month=4, day=27, hour=9))

        self.delete_old_cases(_make_datetime(year=2021, month=1, day=1, hour=9))

        self.assertEqual(Case.objects.all().count(), 1)
        self.assertEqual(Log.objects.all().count(), 3)

    def test_old_case_with_recent_complaint(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date)

        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2014, month=5, day=30, hour=9))
        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2018, month=4, day=27, hour=9))

        complaint_date = _make_datetime(year=2020, month=4, day=27, hour=9)
        eod = make_recipe("legalaid.eod_details", case=case)
        log = make_recipe("cla_auditlog.audit_log")
        make_recipe("complaints.complaint", eod=eod, audit_log=[log], created=complaint_date)

        self.create_event_log_for_case(case, "COMPLAINT_CREATED", complaint_date)

        self.delete_old_cases(_make_datetime(year=2021, month=1, day=1, hour=9))
        self.assertEqual(Case.objects.all().count(), 1)
        self.assertEqual(Complaint.objects.all().count(), 1)
        self.assertEqual(Log.objects.all().count(), 3)
        self.assertEqual(EODDetails.objects.all().count(), 1)

    def test_old_case_with_recent_means_test_change(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date, "legalaid.eligible_case")

        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2014, month=5, day=30, hour=9))
        self.create_event_log_for_case(case, "MT_CHANGED", _make_datetime(year=2020, month=4, day=27, hour=9))

        self.delete_old_cases(_make_datetime(year=2021, month=1, day=1, hour=9))
        self.assertEqual(Case.objects.all().count(), 1)
        self.assertEqual(Log.objects.all().count(), 2)
        self.assertEqual(EligibilityCheck.objects.all().count(), 1)

    def test_old_case_with_two_logs_with_same_date_of_creation(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date, "legalaid.eligible_case")

        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2020, month=4, day=27, hour=9))
        self.create_event_log_for_case(case, "MT_CHANGED", _make_datetime(year=2020, month=4, day=27, hour=9))

        self.delete_old_cases(_make_datetime(year=2021, month=1, day=1, hour=9))
        self.assertEqual(Case.objects.all().count(), 1)
        self.assertEqual(Log.objects.all().count(), 2)
        self.assertEqual(EligibilityCheck.objects.all().count(), 1)

    def test_relatively_new_case_with_no_event_logs(self):
        date = _make_datetime(year=2020, month=4, day=27, hour=9)
        self.create_case(date)

        self.delete_old_cases(_make_datetime(year=2021, month=1, day=1, hour=9))
        self.assertEqual(Case.objects.all().count(), 1)
        self.assertEqual(Log.objects.all().count(), 0)

    def test_old_case_with_no_event_logs(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        self.create_case(date)

        self.delete_old_cases(_make_datetime(year=2021, month=1, day=1, hour=9))
        self.assertEqual(Case.objects.all().count(), 0)
        self.assertEqual(Log.objects.all().count(), 0)
        self.assertEqual(AuditLog.objects.all().count(), 0)
        self.assertEqual(Complaint.objects.all().count(), 0)
        self.assertEqual(EODDetails.objects.all().count(), 0)
        self.assertEqual(EligibilityCheck.objects.all().count(), 0)
        self.assertEqual(DiagnosisTraversal.objects.all().count(), 0)
        self.assertEqual(PersonalDetails.objects.all().count(), 0)

    def test_old_case_with_old_event_logs(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date)

        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2014, month=5, day=30, hour=9))
        self.create_event_log_for_case(case, "CASE_VIEWED", _make_datetime(year=2018, month=4, day=27, hour=9))

        self.delete_old_cases(_make_datetime(year=2021, month=1, day=1, hour=9))
        self.assertEqual(Case.objects.all().count(), 0)
        self.assertEqual(Log.objects.all().count(), 0)
        self.assertEqual(AuditLog.objects.all().count(), 0)
        self.assertEqual(Complaint.objects.all().count(), 0)
        self.assertEqual(EODDetails.objects.all().count(), 0)
        self.assertEqual(EligibilityCheck.objects.all().count(), 0)
        self.assertEqual(DiagnosisTraversal.objects.all().count(), 0)
        self.assertEqual(PersonalDetails.objects.all().count(), 0)

    def test_old_case_with_old_means_test_changed_log(self):
        date = _make_datetime(year=2014, month=4, day=27, hour=9)
        case = self.create_case(date, "legalaid.eligible_case")

        self.create_event_log_for_case(case, "MT_CHANGED", _make_datetime(year=2014, month=5, day=30, hour=9))

        self.delete_old_cases(_make_datetime(year=2021, month=1, day=1, hour=9))
        self.assertEqual(Case.objects.all().count(), 0)
        self.assertEqual(Log.objects.all().count(), 0)
        self.assertEqual(AuditLog.objects.all().count(), 0)
        self.assertEqual(Complaint.objects.all().count(), 0)
        self.assertEqual(EODDetails.objects.all().count(), 0)
        self.assertEqual(EligibilityCheck.objects.all().count(), 0)
        self.assertEqual(DiagnosisTraversal.objects.all().count(), 0)
        self.assertEqual(PersonalDetails.objects.all().count(), 0)
