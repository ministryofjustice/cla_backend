import os
from mock import patch, MagicMock, mock_open
from django.test import TestCase
from reports.views import download_file
from django.conf import settings


class DownloadFileTestCase(TestCase):
    @patch("cla_backend.libs.aws.s3.ReportsS3.get_s3_connection")
    def test_download_no_aws(self, mock_s3):
        # mock pythons open()
        with patch("__builtin__.open", mock_open(read_data="data")) as mock_file:
            mock_request = MagicMock()
            # if file_name contains string "schedule"
            # delete from the database doesn't occur.
            file_name = "scheduled"
            file_path = os.path.join(settings.TEMP_DIR, os.path.basename(file_name))
            settings.AWS_REPORTS_STORAGE_BUCKET_NAME = ""
            settings.DEBUG = True
            # download_file(request, file_name="", *args, **kwargs):
            download_file(mock_request, file_name)
        assert not mock_s3.called
        # Requires string "r" as second argument when
        # built in Open method is called in views.py
        mock_file.assert_called_with(file_path, "r")

    @patch("cla_backend.libs.aws.s3.ReportsS3.get_s3_connection", return_value=MagicMock())
    def test_download_with_aws(self, mock_s3):
        mock_request = MagicMock()
        # if file_name contains string "schedule"
        # delete from the database doesn't occur.
        file_name = "scheduled"
        settings.AWS_REPORTS_STORAGE_BUCKET_NAME = "AWS_TEST"
        # download_file(request, file_name="", *args, **kwargs):
        download_file(mock_request, file_name)
        assert mock_s3.called
