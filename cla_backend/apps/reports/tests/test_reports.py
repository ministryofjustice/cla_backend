import inspect
import datetime
import tempfile
import os

from django.test import TestCase

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
    def test_zip_output(self):
        td = tempfile.mkdtemp()

        OBIEEExporter(td, 'cladev').export()
        self.assertTrue(
            os.path.isfile(os.path.join('%s/cla_database.zip' % td))
        )
