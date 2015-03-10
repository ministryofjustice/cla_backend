# from core.tests.mommy_utils import make_user
# from django.test import TestCase
# from provider.oauth2.models import Client

# from rest_framework import status

# from mohawk import Sender


# class DBExportTestCase(TestCase):

#     CLIENT_ID = '39d31fdffd8c89ebb6d5'
#     CLIENT_SECRET = '7ad5e3cbcdf656ececbd235557f99ec049bee604'

#     def test_export_sql_columns_exist(self):
#         """
#         Basic sanity check to ensure DB export SQL isn't trying to query
#         non-existent tables/columns.
#         """
#         user = make_user()
#         Client.objects.create(
#             name='OBIEE',
#             url='http://localhost/',
#             client_type=0,
#             redirect_uri='http://obiee.localhost/',
#             user=user,
#             client_id=self.CLIENT_ID,
#             client_secret=self.CLIENT_SECRET
#         )
#         # sign request with Mohawk
#         creds = {
#             'id': self.CLIENT_ID,
#             'key': self.CLIENT_SECRET,
#             'algorithm': 'sha256'
#         }

#         host = 'http://testserver'
#         path = '/obiee/dbexport/'
#         params = ('?from=2014-08-28T00:00:00&to=2014-08-28T00:00:01'
#                   '&passphrase=cla')
#         content = ''
#         content_type = ''
#         method = 'GET'

#         sender = Sender(creds, (host + path + params), method, content=content,
#                         content_type=content_type)

#         response = self.client.get((path + params),
#                                    HTTP_AUTHORIZATION=sender.request_header,
#                                    HTTP_CONTENT_TYPE=content_type)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
