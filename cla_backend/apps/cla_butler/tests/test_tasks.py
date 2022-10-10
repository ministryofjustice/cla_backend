from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from cla_butler.tasks import DeleteOldData, get_pks
from core.tests.mommy_utils import make_recipe
from cla_auditlog.models import AuditLog
from complaints.models import Complaint
from legalaid.models import Case, EODDetails, PersonalDetails


class TasksTestCase(TestCase):
    """
    Currently in Django v1.7 database constraint checks are not done until a transaction is committed.
    In TestCase they are never committed so therefore any tests with M2M relationships, such as
    'test_cleanup_personal_details_no_case_attached_successful', are currently passing with a false positive.

    On upgrade to Django v1.8+, check_constraints() is implemented in TestCase so that it will correctly check
    constraints such as M2M relationships and raise an IntegrityError and fail the test.
    The tests should at this point continue to pass.
    """

    def setUp(self):
        super(TasksTestCase, self).setUp()
        self.delete_old_data = DeleteOldData()

    def test_delete_objects(self):
        make_recipe("legalaid.case")
        cases = Case.objects.all()

        self.assertEqual(len(cases), 1)

        self.delete_old_data._delete_objects(cases)

        self.assertEqual(len(Case.objects.all()), 0)

    def test_cleanup_model_from_case_complaints(self):
        case = make_recipe("legalaid.case")
        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod)
        pks = get_pks(Case.objects.all())

        self.assertEqual(len(Complaint.objects.all()), 1)

        self.delete_old_data.cleanup_model_from_case(pks, Complaint, "eod__case_id")

        self.assertEqual(len(Complaint.objects.all()), 0)

    def test_cleanup_model_from_case_eod_details(self):
        case = make_recipe("legalaid.case")
        make_recipe("legalaid.eod_details", case=case)
        pks = get_pks(Case.objects.all())

        self.assertEqual(len(EODDetails.objects.all()), 1)

        self.delete_old_data.cleanup_model_from_case(pks, EODDetails)

        self.assertEqual(len(EODDetails.objects.all()), 0)

    def test_cleanup_personal_details_no_case_attached_successful(self):
        contact_method = make_recipe("legalaid.contact_research_method")
        make_recipe("legalaid.personal_details", contact_for_research_methods=[contact_method])

        self.assertEqual(len(PersonalDetails.objects.all()), 1)

        self.delete_old_data.cleanup_personal_details()

        self.assertEqual(len(PersonalDetails.objects.all()), 0)

    def test_cleanup_case_audit(self):
        log = make_recipe("cla_auditlog.audit_log")
        make_recipe("legalaid.case", audit_log=[log])
        pks = get_pks(Case.objects.all())

        self.assertEqual(len(AuditLog.objects.filter(case__in=pks)), 1)

        self.delete_old_data.cleanup_audit(pks)

        self.assertEqual(len(AuditLog.objects.filter(case__in=pks)), 0)

    def test_cleanup_complaint_audit(self):
        log = make_recipe("cla_auditlog.audit_log")
        case = make_recipe("legalaid.case")
        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod, audit_log=[log])
        pks = get_pks(Case.objects.all())

        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)
        case_complaints = Complaint.objects.filter(eod_id__in=eods).values_list("pk", flat=True)

        self.assertEqual(len(AuditLog.objects.filter(complaint__in=case_complaints)), 1)

        self.delete_old_data.cleanup_audit(pks)

        case_complaints = Complaint.objects.filter(eod_id__in=eods).values_list("pk", flat=True)

        self.assertEqual(len(AuditLog.objects.filter(complaint__in=case_complaints)), 0)

    def test_delete_old_data_over_3_years_successful_delete(self):
        """
        This tests a case over three years without an exclude outcome_code
        """
        log = make_recipe("cla_auditlog.audit_log")

        # Creating a case thats three years old so it gets picked up properly by the delete data
        freezer = freeze_time(timezone.now() + relativedelta(years=-4))
        freezer.start()
        case = make_recipe("legalaid.case", audit_log=[log], outcome_code="CB1")
        freezer.stop()

        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod, audit_log=[log])
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        self.assertEqual(len(Case.objects.all()), 1)
        self.assertEqual(len(AuditLog.objects.filter(case__in=pks)), 1)
        self.assertEqual(len(EODDetails.objects.all()), 1)
        self.assertEqual(len(Complaint.objects.all()), 1)
        case_complaints = Complaint.objects.filter(eod_id__in=eods).values_list("pk", flat=True)
        self.assertEqual(len(AuditLog.objects.filter(complaint__in=case_complaints)), 1)

        self.delete_old_data.run()

        self.assertEqual(len(Case.objects.all()), 0)
        self.assertEqual(len(AuditLog.objects.filter(case__in=pks)), 0)
        self.assertEqual(len(EODDetails.objects.all()), 0)
        self.assertEqual(len(Complaint.objects.all()), 0)
        case_complaints = Complaint.objects.filter(eod_id__in=eods).values_list("pk", flat=True)
        self.assertEqual(len(AuditLog.objects.filter(complaint__in=case_complaints)), 0)

    def test_delete_old_data_run_case_over_3_years_excluded_code_unsuccessful_delete(self):
        """
        This makes sure that even if a case is over 3 years
        its not deleted due to having an excluded outcome_code
        """
        log = make_recipe("cla_auditlog.audit_log")

        # Creating a case thats three years old so it gets picked up properly by the delete data
        freezer = freeze_time(timezone.now() + relativedelta(years=-4))
        freezer.start()
        case = make_recipe("legalaid.case", audit_log=[log], outcome_code="SPOP")
        freezer.stop()

        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod, audit_log=[log])
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        self.assertEqual(len(Case.objects.all()), 1)
        self.assertEqual(len(AuditLog.objects.filter(case__in=pks)), 1)
        self.assertEqual(len(EODDetails.objects.all()), 1)
        self.assertEqual(len(Complaint.objects.all()), 1)
        case_complaints = Complaint.objects.filter(eod_id__in=eods).values_list("pk", flat=True)
        self.assertEqual(len(AuditLog.objects.filter(complaint__in=case_complaints)), 1)

        self.delete_old_data.run()

        self.assertEqual(len(Case.objects.all()), 1)
        self.assertEqual(len(AuditLog.objects.filter(case__in=pks)), 1)
        self.assertEqual(len(EODDetails.objects.all()), 1)
        self.assertEqual(len(Complaint.objects.all()), 1)
        case_complaints = Complaint.objects.filter(eod_id__in=eods).values_list("pk", flat=True)
        self.assertEqual(len(AuditLog.objects.filter(complaint__in=case_complaints)), 1)

    def test_delete_old_data_run_case_under_three_years_unsuccessful_delete(self):
        log = make_recipe("cla_auditlog.audit_log")

        # Creating a case using current timestamp
        case = make_recipe("legalaid.case", audit_log=[log])

        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod, audit_log=[log])
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        self.assertEqual(len(Case.objects.all()), 1)
        self.assertEqual(len(AuditLog.objects.filter(case__in=pks)), 1)
        self.assertEqual(len(EODDetails.objects.all()), 1)
        self.assertEqual(len(Complaint.objects.all()), 1)
        case_complaints = Complaint.objects.filter(eod_id__in=eods).values_list("pk", flat=True)
        self.assertEqual(len(AuditLog.objects.filter(complaint__in=case_complaints)), 1)

        self.delete_old_data.run()

        self.assertEqual(len(Case.objects.all()), 1)
        self.assertEqual(len(AuditLog.objects.filter(case__in=pks)), 1)
        self.assertEqual(len(EODDetails.objects.all()), 1)
        self.assertEqual(len(Complaint.objects.all()), 1)
        case_complaints = Complaint.objects.filter(eod_id__in=eods).values_list("pk", flat=True)
        self.assertEqual(len(AuditLog.objects.filter(complaint__in=case_complaints)), 1)
