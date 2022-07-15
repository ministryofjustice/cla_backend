import mock
from django.test import TestCase
from reports.views import download_file
from django.http import HttpResponse, Http404
from reports.utils import get_s3_connection
from django.conf import settings


class DownloadFileTestCase(TestCase):

    def test_download_no_aws(self):
        # TODO: call method and check it's response
        # When method is called check if a call was made to get_s3_connection
        request = mock.ANY
        file_name = "foo"
        settings.AWS_REPORTS_STORAGE_BUCKET_NAME = False
        # method used in urls.py
        # download_file(request, file_name="", *args, **kwargs):
        # check responses returned
        # check if get_s3_connection was called.
        self.assertEquals(download_file(request, file_name), HttpResponse)



