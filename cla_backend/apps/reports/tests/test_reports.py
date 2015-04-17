import inspect
import datetime
import tempfile
import shutil
from psycopg2 import InternalError
from legalaid.utils.diversity import save_diversity_data
import os

from django.test import TestCase

from core.tests.mommy_utils import make_recipe
import reports.forms
from reports.utils import OBIEEExporter

class ReportsSQLColumnsMatchHeadersTestCase(TestCase):

    def test_headers_count_matches_sql(self):
        for n, i in vars(reports.forms).items():
            if inspect.isclass(i) and issubclass(i, reports.forms.SQLFileDateRangeReport) and i != reports.forms.SQLFileDateRangeReport:
                inst = i(data={'date_from': datetime.datetime.now(), 'date_to': datetime.datetime.now()})
                inst.is_valid()
                inst.get_queryset()
                self.assertEqual(len(inst.description), len(inst.get_headers()), 'Number of columns in %s.get_headers() doesn\'t match the number of columns returned by the sql query.' % n)

            if inspect.isclass(i) and issubclass(i, reports.forms.SQLFileMonthRangeReport) and i != reports.forms.SQLFileMonthRangeReport:
                inst = i(data={'date': datetime.datetime.now()})
                inst.is_valid()
                inst.get_queryset()
                self.assertEqual(len(inst.description), len(inst.get_headers()), 'Number of columns in %s.get_headers() doesn\'t match the number of columns returned by the sql query.' % n)

class ReportsDateRangeValidationWorks(TestCase):

    def test_range_validation_works(self):
        class T(reports.forms.DateRangeReportForm):
            max_date_range = 5

        now = datetime.datetime.now()
        i = T(data={'date_from': now - datetime.timedelta(days=5), 'date_to': now})
        self.assertFalse(i.is_valid())
        self.assertEqual(i.errors, {u'__all__': [u'The date range (6 days, 0:00:00) should span no more than 5 working days']} )
        i2 = T(data={'date_from': now - datetime.timedelta(days=1), 'date_to': now})
        self.assertTrue(i2.is_valid())


class OBIEEExportOutputsZipTestCase(TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp()

        # actually test that it works
        self.personal_details = make_recipe('legalaid.personal_details')
        save_diversity_data(self.personal_details.pk, {'test':'test'})
        self.dt_from = datetime.datetime.now() - datetime.timedelta(days=1)
        self.dt_to = datetime.datetime.now() + datetime.timedelta(days=1)

    def test_zip_output(self):
        e = OBIEEExporter(self.td, 'cla', dt_from=self.dt_from, dt_to=self.dt_to)
        tmp_path = e.tmp_export_path
        e.export()
        self.assertFalse(
            os.path.exists(tmp_path)
        )
        self.assertTrue(
            os.path.isfile(os.path.join('%s/cla_database.zip' % self.td))
        )

    def test_zip_bad_password(self):
        e = OBIEEExporter(self.td, 'wrongpw', dt_from=self.dt_from, dt_to=self.dt_to)
        with self.assertRaises(InternalError):
            e.export()
        self.assertFalse(
            os.path.isfile(os.path.join('%s/cla_database.zip' % self.td))
        )

    def tearDown(self):
        if os.path.exists(self.td):
            shutil.rmtree(self.td, ignore_errors=True)
