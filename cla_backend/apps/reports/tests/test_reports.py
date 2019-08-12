import inspect
import datetime
import os
import shutil
import tempfile

from django.test import TestCase
from psycopg2 import InternalError

import mock

from legalaid.utils.diversity import save_diversity_data
from legalaid.models import Case, EODDetails
from complaints.models import Complaint
from core.tests.mommy_utils import make_recipe
import reports.forms
from reports.utils import OBIEEExporter


class ReportsSQLColumnsMatchHeadersTestCase(TestCase):
    def setUp(self):
        super(ReportsSQLColumnsMatchHeadersTestCase, self).setUp()
        make_recipe("cla_provider.Provider")

    def test_headers_count_matches_sql(self):
        operator = make_recipe("call_centre.operator", is_manager=False, is_cla_superuser=False)
        for n, i in vars(reports.forms).items():
            if (
                inspect.isclass(i)
                and issubclass(i, reports.forms.SQLFileDateRangeReport)
                and i != reports.forms.SQLFileDateRangeReport
            ):
                request = mock.MagicMock(user=operator.user)
                inst = i(
                    data={"date_from": datetime.datetime.now(), "date_to": datetime.datetime.now()}, request=request
                )
                inst.is_valid()
                inst.get_queryset()
                len_desc = len(inst.description)
                len_headers = len(inst.get_headers())
                if inst.__class__.__name__ == "MICaseExtract":
                    # this is due to getting multiple fields as 1 json field in sql
                    len_headers = len_headers - 3
                self.assertEqual(
                    len_desc,
                    len_headers,
                    "Number of columns in %s.get_headers() doesn't match the number of columns returned by the sql query."
                    % n,
                )

            if (
                inspect.isclass(i)
                and issubclass(i, reports.forms.SQLFileMonthRangeReport)
                and i != reports.forms.SQLFileMonthRangeReport
            ):
                inst = i(data={"date": datetime.datetime.now()})
                inst.is_valid()
                inst.get_queryset()
                self.assertEqual(
                    len(inst.description),
                    len(inst.get_headers()),
                    "Number of columns in %s.get_headers() doesn't match the number of columns returned by the sql query."
                    % n,
                )


class ReportsDateRangeValidationWorks(TestCase):
    def test_range_validation_works(self):
        class T(reports.forms.DateRangeReportForm):
            max_date_range = 5

        now = datetime.datetime.now()
        i = T(data={"date_from": now - datetime.timedelta(days=5), "date_to": now})
        self.assertFalse(i.is_valid())
        self.assertEqual(
            i.errors, {u"__all__": [u"The date range (6 days, 0:00:00) should span no more than 5 working days"]}
        )
        i2 = T(data={"date_from": now - datetime.timedelta(days=1), "date_to": now})
        self.assertTrue(i2.is_valid())


class MIDuplicateCasesTestCase(TestCase):
    def test_duplicate_cases(self):
        # random data
        for _ in range(20):
            personal_details = make_recipe(
                "legalaid.personal_details", _fill_optional=["full_name", "date_of_birth", "postcode"]
            )
            make_recipe("legalaid.case", personal_details=personal_details)

        # data with one pair of duplicates
        data = (
            dict(full_name="Mary Smith", date_of_birth=datetime.date(1980, 5, 1), postcode="SW1A 1AA"),
            dict(full_name="Mary Smith", date_of_birth=datetime.date(1975, 4, 10), postcode="SW1A 1AA"),
            dict(full_name="mary smith", date_of_birth=datetime.date(1980, 5, 1), postcode="sw1a1aa"),
        )
        for details in data:
            personal_details = make_recipe("legalaid.personal_details", **details)
            make_recipe("legalaid.case", personal_details=personal_details)

        self.assertEqual(Case.objects.count(), 23)

        form = reports.forms.MIDuplicateCaseExtract(
            data={"date_from": datetime.date.today() - datetime.timedelta(days=1), "date_to": datetime.date.today()}
        )
        self.assertTrue(form.is_valid())
        query_result = form.get_queryset()
        self.assertEqual(len(query_result), 2)
        saved_data = [list(row[-3:]) for row in query_result]
        self.assertListEqual(
            saved_data,
            [
                ["mary smith", datetime.date(1980, 5, 1), "sw1a1aa"],
                ["Mary Smith", datetime.date(1980, 5, 1), "SW1A 1AA"],
            ],
        )


class OBIEEExportOutputsZipTestCase(TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp()

        # actually test that it works
        self.personal_details = make_recipe("legalaid.personal_details")
        save_diversity_data(self.personal_details.pk, {"test": "test"})
        self.dt_from = datetime.datetime.now() - datetime.timedelta(days=1)
        self.dt_to = datetime.datetime.now() + datetime.timedelta(days=1)

    def test_zip_output(self):
        e = OBIEEExporter(self.td, "cla", dt_from=self.dt_from, dt_to=self.dt_to)
        tmp_path = e.tmp_export_path
        e.export()
        self.assertFalse(os.path.exists(tmp_path))
        self.assertTrue(os.path.isfile(os.path.join("%s/cla_database.zip" % self.td)))

    def test_zip_bad_password(self):
        e = OBIEEExporter(self.td, "wrongpw", dt_from=self.dt_from, dt_to=self.dt_to)
        with self.assertRaises(InternalError):
            e.export()
        self.assertFalse(os.path.isfile(os.path.join("%s/cla_database.zip" % self.td)))

    def tearDown(self):
        if os.path.exists(self.td):
            shutil.rmtree(self.td, ignore_errors=True)


class AbstractExportWithOrganisation(object):
    def __init__(self, *args, **kwargs):
        super(AbstractExportWithOrganisation, self).__init__(*args, **kwargs)
        self.form_class = None
        self.model_class = None
        self.foo_org = None
        self.foo_org_operator = None
        self.bar_org = None
        self.bar_org_operator = None
        self.no_org_operator = None

    def setUp(self, *args, **kwargs):
        super(AbstractExportWithOrganisation, self).setUp(*args, **kwargs)
        self.foo_org = make_recipe("call_centre.organisation", name="Organisation Foo")
        self.foo_org_operator = make_recipe(
            "call_centre.operator", is_manager=False, is_cla_superuser=False, organisation=self.foo_org
        )
        self.create_models(self.foo_org_operator)

        self.bar_org = make_recipe("call_centre.organisation", name="Organisation Bar")
        self.bar_org_operator = make_recipe(
            "call_centre.operator", is_manager=False, is_cla_superuser=False, organisation=self.bar_org
        )
        self.create_models(self.bar_org_operator)

        self.no_org_operator = make_recipe("call_centre.operator", is_manager=False, is_cla_superuser=False)
        self.create_models(self.no_org_operator)

    def create_models(self, operator):
        raise NotImplementedError

    def assert_organisations_in_results(self, organisations, results, organisation_index):
        for result in results:
            self.assertIn(result[organisation_index], organisations)

    def test_operator_manager_can_export_report_for_own_organisation(self):
        self.assertEqual(self.model_class.objects.count(), 3)

        form = self.form_class(
            user=self.foo_org_operator.user,
            data={"date_from": datetime.date.today(), "date_to": datetime.date.today()},
        )

        self.assertTrue(form.is_valid())
        query_result = form.get_queryset()
        self.assertEqual(len(query_result), 2)
        self.assert_organisations_in_results(
            [self.foo_org.name, None], query_result, form.get_organisation_column_index()
        )

    def test_operator_manager_without_org_can_export_all(self):
        self.assertEqual(self.model_class.objects.count(), 3)

        form = self.form_class(
            user=self.no_org_operator.user, data={"date_from": datetime.date.today(), "date_to": datetime.date.today()}
        )

        self.assertTrue(form.is_valid())
        query_result = form.get_queryset()
        self.assertEqual(len(query_result), 3)
        self.assert_organisations_in_results(
            [self.foo_org.name, self.bar_org.name, None], query_result, form.get_organisation_column_index()
        )

    def test_cla_superuser_without_all(self):
        self.assertEqual(self.model_class.objects.count(), 3)
        cla_superuser = make_recipe("call_centre.operator", is_manager=False, is_cla_superuser=True)
        form = self.form_class(
            user=cla_superuser.user, data={"date_from": datetime.date.today(), "date_to": datetime.date.today()}
        )

        self.assertTrue(form.is_valid())
        query_result = form.get_queryset()
        self.assertEqual(len(query_result), 3)
        self.assert_organisations_in_results(
            [self.foo_org.name, self.bar_org.name, None], query_result, form.get_organisation_column_index()
        )


class EODDetailsExportTestCase(AbstractExportWithOrganisation, TestCase):
    def __init__(self, methodName=""):
        super(EODDetailsExportTestCase, self).__init__(methodName)
        self.form_class = reports.forms.MIEODReport
        self.model_class = EODDetails

    def create_models(self, operator):
        personal_details = make_recipe(
            "legalaid.personal_details", _fill_optional=["full_name", "date_of_birth", "postcode"]
        )
        case = make_recipe("legalaid.case", personal_details=personal_details, created_by=operator.user)
        make_recipe("legalaid.eod_details", notes="EOD notes", case=case)


class ComplaintsExportTestCase(AbstractExportWithOrganisation, TestCase):
    def __init__(self, methodName=""):
        super(ComplaintsExportTestCase, self).__init__(methodName)
        self.form_class = reports.forms.ComplaintsReport
        self.model_class = Complaint

    def create_models(self, operator):
        personal_details = make_recipe(
            "legalaid.personal_details", _fill_optional=["full_name", "date_of_birth", "postcode"]
        )
        case = make_recipe("legalaid.case", personal_details=personal_details, created_by=operator.user)
        eod = make_recipe("legalaid.eod_details", notes="EOD notes", case=case)
        make_recipe("complaints.complaint", eod=eod)
