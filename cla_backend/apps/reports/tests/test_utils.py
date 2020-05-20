import mock
import os

from boto.s3.connection import S3Connection
from django.test import TestCase, override_settings
from reports.utils import get_s3_connection


class UtilsTestCase(TestCase):
    @override_settings(AWS_ACCESS_KEY_ID="000000000001", AWS_SECRET_ACCESS_KEY="000000000002")
    def test_get_s3_connection(self):
        envs = {"AWS_S3_HOST": "s3.eu-west-2.amazonaws.com", "S3_USE_SIGV4": "True"}
        with mock.patch.dict(os.environ, envs):
            conn = get_s3_connection()
            self.assertIsInstance(conn, S3Connection)
