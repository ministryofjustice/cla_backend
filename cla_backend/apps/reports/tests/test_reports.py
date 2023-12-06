import inspect
import datetime
import os
import shutil
import tempfile
from itertools import cycle

from django.test import TestCase
from psycopg2 import InternalError

from cla_common.constants import CONTACT_SAFETY, REASONS_FOR_CONTACTING
from core.tests.mommy_utils import make_recipe
from legalaid.utils.diversity import save_diversity_data
import reports.forms
from reports.utils import OBIEEExporter

from freezegun import freeze_time

from cla_auditlog.models import AuditLog
from checker.models import ReasonForContacting


class ReportsSQLColumnsMatchHeadersTestCase(TestCase):
    def setUp(self):
        super(ReportsSQLColumnsMatchHeadersTestCase, self).setUp()
        make_recipe("cla_provider.Provider")

    def test_headers_count_matches_sql(self):
        for n, i in vars(reports.forms).items():
            if (
                inspect.isclass(i)
                and issubclass(i, reports.forms.SQLFileDateRangeReport)
                and i != reports.forms.SQLFileDateRangeReport
            ):
                inst = i(data={"date_from": datetime.datetime.now(), "date_to": datetime.datetime.now()})
                inst.is_valid()
                inst.get_queryset()
                len_desc = len(inst.description)
                len_headers = len(inst.get_headers())
                if inst.__class__.__name__ in ["MICaseExtract", "MICaseExtractExtended", "CaseDemographicsReport"]:
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


class ReportOrganisationColumnTestCase(TestCase):
    def test_mi_survey_dom1_extract_organisation_column(self):
        pd = make_recipe("legalaid.personal_details", safe_to_contact=CONTACT_SAFETY.SAFE, contact_for_research=True)
        foo_org = make_recipe("call_centre.organisation", name="Foo org")
        bar_org = make_recipe("call_centre.organisation", name="Bar org")
        make_recipe("legalaid.case", personal_details=pd, organisation=foo_org)
        make_recipe("legalaid.case", personal_details=pd, organisation=bar_org)
        data = {"date_from": datetime.datetime.now(), "date_to": datetime.datetime.now()}
        instance = reports.forms.MISurveyExtract(data=data)
        instance.is_valid()
        results = instance.get_queryset()
        self.assertEqual(len(results), 1)

        columns = [column.lower() for column in instance.get_headers()]
        index = columns.index("organisation")
        self.assertEqual("Bar org, Foo org", results[0][index])


class ReportMiAuditLogExtractTestCase(TestCase):
    def test_mi_case_audit_log_extract(self):
        def get_expected(model, operator, audit):
            return (
                model.reference,
                AuditLog.ACTIONS.VIEWED,
                operator.user.username,
                operator.organisation.name,
                audit.created,
            )

        self._test_model_audit_log_("legalaid.case", reports.forms.MIExtractCaseViewAuditLog, get_expected)

    def test_mi_complaint_audit_log_extract(self):
        def get_expected(model, operator, audit):
            return (
                model.eod.case.reference,
                model.pk,
                AuditLog.ACTIONS.VIEWED,
                operator.user.username,
                operator.organisation.name,
                audit.created,
            )

        self._test_model_audit_log_("complaints.complaint", reports.forms.MIExtractComplaintViewAuditLog, get_expected)

    def _test_model_audit_log_(self, model_def, form_cls, get_expected):
        dates = {"date_from": datetime.datetime.now(), "date_to": datetime.datetime.now()}

        foo_org = make_recipe("call_centre.organisation", name="Foo org")
        bar_org = make_recipe("call_centre.organisation", name="Bar org")

        operator1 = make_recipe("call_centre.operator", organisation=foo_org)
        operator2 = make_recipe("call_centre.operator", organisation=bar_org)
        operators = [operator1, operator2]

        models = [make_recipe(model_def), make_recipe(model_def)]
        expected_results = []
        for model in models:
            for operator in operators:
                audit = make_recipe("cla_auditlog.audit_log", user=operator.user, action=AuditLog.ACTIONS.VIEWED)
                model.audit_log.add(audit)
                expected_results.append(get_expected(model, operator, audit))

        instance = form_cls(data=dates)
        instance.is_valid()
        results = instance.get_queryset()
        self.assertEqual(len(results), 4)
        self.assertEqual(results, list(reversed(expected_results)))


class ReportsDateRangeValidationWorks(TestCase):
    def test_valid_date_range(self):
        class T(reports.forms.DateRangeReportForm):
            max_date_range = 5

        now = datetime.datetime.now()
        i = T(data={"date_from": now - datetime.timedelta(days=4), "date_to": now})
        self.assertTrue(i.is_valid())
        self.assertEqual(i.errors.keys(), [])

    def test_invalid_date_range(self):
        class T(reports.forms.DateRangeReportForm):
            max_date_range = 5

        now = datetime.datetime.now()
        i = T(data={"date_from": now - datetime.timedelta(days=5), "date_to": now})
        self.assertFalse(i.is_valid())
        self.assertEqual(i.errors.keys(), ["__all__"])
        self.assertEqual(len(i.errors["__all__"]), 1)
        self.assertIn(
            i.errors[u"__all__"][0],
            [
                u"The date range (6 days, 0:00:00) should span no more than 5 working days",
                u"The date range (6 days, 1:00:00) should span no more than 5 working days",
                u"The date range (5 days, 23:00:00) should span no more than 5 working days",
            ],
        )

    def test_end_date_before_start_date(self):
        class T(reports.forms.DateRangeReportForm):
            max_date_range = 5

        from_ = datetime.datetime.now()
        to = from_ - datetime.timedelta(days=3)
        i = T(data={"date_from": from_, "date_to": to})
        self.assertFalse(i.is_valid())
        self.assertEqual(i.errors.keys(), ["__all__"])
        self.assertEqual(len(i.errors["__all__"]), 1)
        error_string = "'Date from' (%s) should be before or equal to 'Date to' (%s)" % (
            from_.strftime("%d/%m/%Y"),
            to.strftime("%d/%m/%Y"),
        )
        self.assertEqual(str(i.errors[u"__all__"][0]), error_string)

    def test_valid_date_range_clocks_going_forward(self):
        class T(reports.forms.DateRangeReportForm):
            max_date_range = 5

        start = datetime.datetime(2019, 3, 29)  # GMT
        end = datetime.datetime(2019, 4, 2)  # BST
        i = T(data={"date_from": start, "date_to": end})
        self.assertTrue(i.is_valid())

    def test_valid_date_range_clocks_going_back(self):
        class T(reports.forms.DateRangeReportForm):
            max_date_range = 5

        start = datetime.datetime(2019, 10, 25)  # BST
        end = datetime.datetime(2019, 10, 29)  # GMT
        i = T(data={"date_from": start, "date_to": end})
        self.assertTrue(i.is_valid())

    def test_invalid_date_range_clocks_going_forward(self):
        class T(reports.forms.DateRangeReportForm):
            max_date_range = 5

        start = datetime.datetime(2019, 3, 29)  # GMT
        end = datetime.datetime(2019, 4, 3)  # BST
        i = T(data={"date_from": start, "date_to": end})
        self.assertFalse(i.is_valid())

    def test_invalid_date_range_clocks_going_back(self):
        class T(reports.forms.DateRangeReportForm):
            max_date_range = 5

        start = datetime.datetime(2019, 10, 25)  # BST
        end = datetime.datetime(2019, 10, 30)  # GMT
        i = T(data={"date_from": start, "date_to": end})
        self.assertFalse(i.is_valid())


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

        from legalaid.models import Case

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


class TestKnowledgeBaseArticlesExport(TestCase):
    def setUp(self):
        article_1, article_2, article_3, article4 = make_recipe("knowledgebase.article", _quantity=4)
        make_recipe("knowledgebase.telephone_number", article=article_1, number=123)
        make_recipe("knowledgebase.telephone_number", article=article_1, number=456, name="special")
        make_recipe("knowledgebase.telephone_number", article=article_2, number=789)
        make_recipe("knowledgebase.article_category_matrix", article=article_1, article_category__name="a category")
        make_recipe(
            "knowledgebase.article_category_matrix",
            article=article_1,
            article_category__name="another category",
            preferred_signpost=True,
        )

    def test_queries(self):
        with self.assertNumQueries(4):  # Articles + prefetch_related of phone numbers and article categories
            reports.forms.AllKnowledgeBaseArticles().get_output()

    def test_lengths(self):
        output = reports.forms.AllKnowledgeBaseArticles().get_output()
        self.assertEqual([len(row) for row in output], [39] * 5)

    def test_values(self):
        output = reports.forms.AllKnowledgeBaseArticles().get_output()
        # phone number with no name; phone number with a name; no third phone number
        self.assertEqual(output[1][19:25], ["", "123", "special", "456", "", ""])
        # third number is on the second article
        self.assertEqual(output[2][19:25], ["", "789", "", "", "", ""])
        # category name; article is not preferred signpost; second category name; article is preferred signpost; no third category
        self.assertEqual(output[1][27:33], ["a category", False, "another category", True, "", ""])


class ReasonForContactingReportTestCase(TestCase):
    def setUp(self):
        self.referrers = [
            "Unknown",
            "https://localhost/scope/diagnosis",
            "https://localhost/scope/diagnosis/n131",
            "https://localhost/scope/diagnosis?category=check",
            "https://localhost/scope/diagnosis",
        ]

    def test_rfc(self):
        categories = [
            REASONS_FOR_CONTACTING.MISSING_PAPERWORK,
            REASONS_FOR_CONTACTING.MISSING_PAPERWORK,
            REASONS_FOR_CONTACTING.DIFFICULTY_ONLINE,
            REASONS_FOR_CONTACTING.HOW_SERVICE_HELPS,
            REASONS_FOR_CONTACTING.PNS,
        ]

        cases = [make_recipe("legalaid.case"), make_recipe("legalaid.case"), make_recipe("legalaid.case"), None, None]
        resources = make_recipe(
            "checker.reasonforcontacting", referrer=cycle(self.referrers), case=cycle(cases), _quantity=5
        )

        make_recipe(
            "checker.reasonforcontacting_category",
            reason_for_contacting=cycle(resources),
            category=cycle(categories),
            _quantity=5,
        )
        make_recipe(
            "checker.reasonforcontacting_category",
            reason_for_contacting=resources[-1],
            category=REASONS_FOR_CONTACTING.PNS,
        )

        # Make a few categories that were created in the distant paste
        freezer = freeze_time("2023-10-01 11:00")
        freezer.start()
        day_ago_resources = make_recipe(
            "checker.reasonforcontacting", referrer=cycle(self.referrers), case=cycle(cases), _quantity=5
        )
        make_recipe(
            "checker.reasonforcontacting_category",
            reason_for_contacting=cycle(day_ago_resources),
            category=cycle(categories),
            _quantity=5,
        )
        freezer.stop()

        # Generate report with date range
        stats = ReasonForContacting.get_report_category_stats(
            datetime.datetime.now() - datetime.timedelta(hours=1), datetime.datetime.now()
        )
        expected_stats = {
            REASONS_FOR_CONTACTING.MISSING_PAPERWORK: {"count": 2, "with_cases": 2, "without_cases": 0},
            REASONS_FOR_CONTACTING.DIFFICULTY_ONLINE: {"count": 1, "with_cases": 1, "without_cases": 0},
            REASONS_FOR_CONTACTING.HOW_SERVICE_HELPS: {"count": 1, "with_cases": 0, "without_cases": 1},
            REASONS_FOR_CONTACTING.PNS: {"count": 2, "with_cases": 0, "without_cases": 2},
        }
        expected_others = {"count": 0, "with_cases": 0, "without_cases": 0}
        for stat in stats["categories"]:
            expected = expected_stats[stat["key"]] if stat["key"] in expected_stats else expected_others
            actual = {"count": stat["count"], "with_cases": stat["with_cases"], "without_cases": stat["without_cases"]}
            self.assertDictEqual(expected, actual)

    def test_report_stats_cases_referrer(self):
        # Make a few reason for contacting records that were created in the distant paste
        freezer = freeze_time("2023-10-01 10:00")
        freezer.start()
        categories = [
            REASONS_FOR_CONTACTING.PNS,
            REASONS_FOR_CONTACTING.AREA_NOT_COVERED,
            REASONS_FOR_CONTACTING.HOW_SERVICE_HELPS,
            REASONS_FOR_CONTACTING.DIFFICULTY_ONLINE,
            REASONS_FOR_CONTACTING.PREFER_SPEAKING,
        ]
        # Create reason for contacting records that we don't care about, for noise purpose
        resources = make_recipe("checker.reasonforcontacting", referrer=cycle(self.referrers), _quantity=5)
        make_recipe(
            "checker.reasonforcontacting_category",
            reason_for_contacting=cycle(resources),
            category=cycle(categories),
            _quantity=5,
        )

        # Create records with our test referrer that we are interested in
        test_referrer = "https://i.am.referrer"
        categories = [
            REASONS_FOR_CONTACTING.CANT_ANSWER,
            REASONS_FOR_CONTACTING.CANT_ANSWER,
            REASONS_FOR_CONTACTING.CANT_ANSWER,
        ]
        cases = [make_recipe("legalaid.case"), make_recipe("legalaid.case"), None]
        resources = make_recipe("checker.reasonforcontacting", case=cycle(cases), referrer=test_referrer, _quantity=3)
        make_recipe(
            "checker.reasonforcontacting_category",
            reason_for_contacting=cycle(resources),
            category=cycle(categories),
            _quantity=3,
        )
        date_from = datetime.datetime.now() - datetime.timedelta(hours=1)
        date_to = date_from + datetime.timedelta(hours=2)
        freezer.stop()

        stats = ReasonForContacting.get_report_category_stats(
            start_date=date_from, end_date=date_to, referrer=test_referrer
        )
        cant_answer_stats = {}
        for stat in stats["categories"]:
            if stat["key"] == REASONS_FOR_CONTACTING.CANT_ANSWER:
                cant_answer_stats = stat
                break

        self.assertTrue(cant_answer_stats, "Could not find expected category")
        self.assertEqual(stats["total_count"], 3)
        self.assertEqual(cant_answer_stats["with_cases"], 2)
        self.assertEqual(cant_answer_stats["without_cases"], 1)
