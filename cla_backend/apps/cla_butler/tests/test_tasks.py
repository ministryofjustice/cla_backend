import os

import mock
from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from cla_butler.constants import delete_option_three_years, delete_option_no_personal_details
from cla_butler.tasks import DeleteOldData, get_pks, DiversityDataCheckTask, DiversityDataReencryptTask
from core.tests.mommy_utils import make_recipe
from cla_auditlog.models import AuditLog
from complaints.models import Complaint
from legalaid.models import Case, EODDetails, PersonalDetails
from cla_butler.models import DiversityDataCheck, ACTION, STATUS
from cla_butler.tests.mixins import CreateSampleDiversityData
from legalaid.utils import diversity


def mock_load_diversity_data(personal_details_pk, passphrase):
    if personal_details_pk % 2 == 0:
        raise ValueError("Something went wrong")


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

    def data_deletion_check(self, primary_keys, eods, before_data_count, after_data_count, delete_option):
        """
        Checks the data before, runs the delete_old_data command and then checks
        the data afterwards to see if it has been deleted/not deleted
        """
        self.assertEqual(len(Case.objects.all()), before_data_count)
        self.assertEqual(len(AuditLog.objects.filter(case__in=primary_keys)), before_data_count)
        self.assertEqual(len(EODDetails.objects.all()), before_data_count)
        self.assertEqual(len(Complaint.objects.all()), before_data_count)
        case_complaints = Complaint.objects.filter(eod_id__in=eods).values_list("pk", flat=True)
        self.assertEqual(len(AuditLog.objects.filter(complaint__in=case_complaints)), before_data_count)
        # Pass in string parameters with which test to run.
        self.delete_old_data.run(delete_option)

        self.assertEqual(len(Case.objects.all()), after_data_count)
        self.assertEqual(len(AuditLog.objects.filter(case__in=primary_keys)), after_data_count)
        self.assertEqual(len(EODDetails.objects.all()), after_data_count)
        self.assertEqual(len(Complaint.objects.all()), after_data_count)
        case_complaints = Complaint.objects.filter(eod_id__in=eods).values_list("pk", flat=True)
        self.assertEqual(len(AuditLog.objects.filter(complaint__in=case_complaints)), after_data_count)

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

        self.data_deletion_check(pks, eods, 1, 0, delete_option_three_years)

    def test_delete_old_data_run_case_over_3_years_excluded_code_unsuccessful_delete(self):
        """
        This makes sure that even if a case is over 3 years
        its not deleted due to having an excluded outcome_code
        """
        log = make_recipe("cla_auditlog.audit_log")

        count = 0
        for code in self.delete_old_data.OUTCOME_CODES:
            count += 1
            freezer = freeze_time(timezone.now() + relativedelta(years=-4))
            freezer.start()
            case = make_recipe("legalaid.case", audit_log=[log], outcome_code=code)
            freezer.stop()

            eod = make_recipe("legalaid.eod_details", case=case)
            make_recipe("complaints.complaint", eod=eod, audit_log=[log])
            pks = get_pks(Case.objects.all())
            eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

            self.data_deletion_check(pks, eods, count, count, delete_option_three_years)

    def test_delete_old_data_run_case_under_three_years_unsuccessful_delete(self):
        log = make_recipe("cla_auditlog.audit_log")

        # Creating a case using current timestamp
        case = make_recipe("legalaid.case", audit_log=[log], outcome_code="SPOP")

        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod, audit_log=[log])
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        self.data_deletion_check(pks, eods, 1, 1, delete_option_three_years)

    def test_delete_no_personal_details_success(self):
        """
        This tests a case with no personal details is removed successfully.
        There are no personal details, notes, or provider notes.
        Conditions met to delete data.
        """
        self.setup_personal_details_test(3, True, "", "")
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        self.data_deletion_check(pks, eods, 1, 0, delete_option_no_personal_details)

    def test_delete_personal_details_unsuccessful(self):
        """
        This test case is greater than 2 weeks old, but there is personal data.
        Should not delete as there is personal data.
        """
        self.setup_personal_details_test(3, False, "foo", "bar")
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        self.data_deletion_check(pks, eods, 1, 1, delete_option_no_personal_details)

    def test_delete_no_personal_details_contains_notes_unsuccessful(self):
        """
        This test case is greater than 2 weeks old, but there is no personal data.
        However, the notes is not empty, so delete conditions are not met.
        """
        self.setup_personal_details_test(3, True, "foo", "")
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        self.data_deletion_check(pks, eods, 1, 1, delete_option_no_personal_details)

    def test_delete_no_personal_details_contains_provider_notes_unsuccessful(self):
        """
        This test case is greater than 2 weeks old, but there is no personal data.
        However, the provider notes are not empty, so delete conditions are not met.
        """
        self.setup_personal_details_test(3, True, "", "foo")
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        self.data_deletion_check(pks, eods, 1, 1, delete_option_no_personal_details)

    def test_delete_no_personal_details_2_weeks_old_unsuccessful(self):
        """
        This tests a case should be not be deleted because it's only one week old.
        """
        self.setup_personal_details_test(1, True, "", "")
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        self.data_deletion_check(pks, eods, 1, 1, delete_option_no_personal_details)

    def test_delete_no_personal_details_2_weeks_old_success(self):
        """
        This tests a case should be deleted when its greater that 2 weeks old
        and meets conditions to delete.
        """
        self.setup_personal_details_test(3, True, "", "")
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        self.data_deletion_check(pks, eods, 1, 0, delete_option_no_personal_details)

    def test_delete_no_personal_details_no_notes_2_weeks_old_success(self):
        """
        This tests a case should be deleted when its greater that 2 weeks old
        and meets conditions to delete - specifically no notes no provider details.
        """
        self.setup_personal_details_test(3, True, "", "")
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        self.data_deletion_check(pks, eods, 1, 0, delete_option_no_personal_details)

    def test_delete_incorrect_delete_option_argument_passed(self):
        """
        This tests when an incorrect delete option has been passed
        then an exception is raised.
        """
        self.setup_personal_details_test(3, True, "", "")
        pks = get_pks(Case.objects.all())
        eods = EODDetails.objects.filter(case_id__in=pks).values_list("pk", flat=True)

        # Check that an exception was raised because of incorrect delete option argument
        with self.assertRaises(Exception):
            # pass foo as an incorrect argument
            self.data_deletion_check(pks, eods, 1, 1, "Foo")

    def setup_personal_details_test(self, weeks, no_personal_data, notes, provider_notes):
        """
        Method to set up recipes needed for no personal data tests
        """
        log = make_recipe("cla_auditlog.audit_log")
        freezer = freeze_time(timezone.now() + relativedelta(weeks=-weeks))
        freezer.start()

        if no_personal_data:
            # personal details are auto generated, so set to None to be empty
            case = make_recipe(
                "legalaid.case", audit_log=[log], personal_details=None, notes=notes, provider_notes=provider_notes
            )
        else:
            # Personal details are already populated.
            case = make_recipe("legalaid.case", audit_log=[log], notes=notes, provider_notes=provider_notes)

        freezer.stop()
        eod = make_recipe("legalaid.eod_details", case=case)
        make_recipe("complaints.complaint", eod=eod, audit_log=[log])


class DiversityDataCheckTaskTestCase(CreateSampleDiversityData, TestCase):
    @mock.patch("legalaid.utils.diversity.load_diversity_data", mock_load_diversity_data)
    def test_run(self):
        DiversityDataCheckTask().run("cla", 0, 1000, description="")
        success_count = DiversityDataCheck.objects.filter(action=ACTION.CHECK, status=STATUS.OK).count()
        failure_count = DiversityDataCheck.objects.filter(action=ACTION.CHECK, status=STATUS.FAIL).count()
        failure_messages = list(
            DiversityDataCheck.objects.filter(action=ACTION.CHECK, status=STATUS.FAIL).values_list("detail", flat=True)
        )
        expected_failure_messages = [u"Something went wrong"] * 5
        self.assertEqual(success_count, 5)
        self.assertEqual(failure_count, 5)
        self.assertEqual(failure_messages, expected_failure_messages)


class DiversityDataReencryptTaskTestCase(CreateSampleDiversityData, TestCase):
    def get__key(self, key_name):
        file_path = os.path.join(os.path.dirname(diversity.__file__), "keys", key_name)
        with open(file_path) as f:
            return f.read()

    def test_run(self):
        previous_key = diversity.get_private_key()
        mock_keys = {
            "PREVIOUS_DIVERSITY_PRIVATE_KEY": previous_key,
            "DIVERSITY_PRIVATE_KEY": self.get__key("diversity_dev_reencrypt_private.key"),
            "DIVERSITY_PUBLIC_KEY": self.get__key("diversity_dev_reencrypt_public.key"),
        }
        with mock.patch.dict(os.environ, mock_keys):
            ids_to_reencrypt = self.pd_records_ids[0:5]
            DiversityDataReencryptTask().run("cla", ids_to_reencrypt)
            qs = DiversityDataCheck.objects.filter(action=ACTION.REENCRYPT, status=STATUS.OK)
            reencrypted_items = list(qs.values_list("personal_details_id", flat=True))
            self.assertListEqual(ids_to_reencrypt, reencrypted_items)
