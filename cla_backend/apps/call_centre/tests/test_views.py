from django.test import TestCase
from django.conf.urls import patterns, url

from rest_framework import permissions
from rest_framework import status

from call_centre.views import DBExportView


class MockDBExportView(DBExportView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)


urlpatterns = patterns('',
    url(r'^mock_dbexport/$',
        MockDBExportView.as_view(),
        name='mock_db_export')
)


class DBExportTestCase(TestCase):
    urls = 'call_centre.tests.test_views'

    def test_export_sql_columns_exist(self):
        """
        Basic sanity check to ensure DB export SQL isn't trying to query
        non-existent tables/columns.
        """
        response = self.client.get('/mock_dbexport/?passphrase=cla&from=2014-01-01T00:00:00&to=2014-12-31T23:59:59')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
