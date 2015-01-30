from django.test import TestCase

from rest_framework import status

from mohawk import Sender


class DBExportTestCase(TestCase):
    fixtures = ['test_auth_clients']

    def test_export_sql_columns_exist(self):
        """
        Basic sanity check to ensure DB export SQL isn't trying to query
        non-existent tables/columns.
        """

        # sign request with Mohawk
        creds = {
            'id': '39d31fdffd8c89ebb6d5',
            'key': '7ad5e3cbcdf656ececbd235557f99ec049bee604',
            'algorithm': 'sha256'
        }

        host = 'http://testserver'
        path = '/obiee/dbexport/'
        params = ('?from=2014-08-28T00:00:00&to=2014-08-28T00:00:01'
                  '&passphrase=cla')
        content = ''
        content_type = ''
        method = 'GET'

        sender = Sender(creds, (host + path + params), method, content=content,
                        content_type=content_type)

        response = self.client.get((path + params),
                                   HTTP_AUTHORIZATION=sender.request_header,
                                   HTTP_CONTENT_TYPE=content_type)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
