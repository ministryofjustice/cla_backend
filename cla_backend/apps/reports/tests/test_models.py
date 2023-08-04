from mock import MagicMock, patch
from django.test import TestCase
from reports.models import delete_export_file
from django.conf import settings


class DeleteExportFile(TestCase):
    @patch("cla_backend.libs.aws.s3.ReportsS3.get_s3_connection")
    def test_delete_export_file_no_aws(self, mock_s3):
        with patch("os.remove") as mock_remove:
            settings.AWS_REPORTS_STORAGE_BUCKET_NAME = ""
            sender = MagicMock()
            instance = MagicMock()
            # delete_export_file(sender, instance=None, **kwargs)
            delete_export_file(sender, instance)
            assert mock_remove.called
            assert not mock_s3.called

    @patch("cla_backend.libs.aws.s3.ReportsS3.get_s3_connection", return_value=MagicMock())
    def test_delete_export_file_with_aws(self, mock_s3):
        settings.AWS_REPORTS_STORAGE_BUCKET_NAME = "AWS_TEST"
        sender = MagicMock()
        instance = MagicMock()
        instance.path = "/tmp/test.txt"
        delete_export_file(sender, instance)
        assert mock_s3.called
