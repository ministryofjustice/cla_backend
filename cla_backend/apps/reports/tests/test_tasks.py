import mock
import datetime
import json
from psycopg2 import InternalError
from django.test import TestCase
from reports.tasks import OBIEEExportTask
from core.tests.mommy_utils import make_user, make_recipe
from legalaid.utils.diversity import save_diversity_data


class OBIEEExportTaskTestCase(TestCase):
    def setUp(self):
        self.personal_details = make_recipe("legalaid.personal_details")
        save_diversity_data(self.personal_details.pk, {"test": "test"})

        self.task = OBIEEExportTask()
        self.task._create_export = mock.MagicMock()
        self.task.send_to_s3 = mock.MagicMock()
        self.user = make_user()

    def run_task(self, passphrase):
        today = datetime.datetime.today()
        filename = "cla.database.zip"
        post_data = {"action": "Export", "date_month": today.month, "date_year": today.year, "passphrase": passphrase}
        post_data = json.dumps(post_data)
        form_class_name = "MIOBIEEExportExtract"
        self.task.run(user_id=self.user.id, form_class_name=form_class_name, post_data=post_data, filename=filename)

    def test_bad_passphrase_message(self):
        with self.assertRaisesMessage(InternalError, "Wrong key or corrupt data"):
            self.run_task("badpass")
        self.assertEqual("Check passphrase and try again", self.task.message)

    def test_message_reset_per_run(self):
        # Run task with an invalid passphrase
        with self.assertRaisesMessage(InternalError, "Wrong key or corrupt data"):
            self.run_task("badpass")
        self.assertEqual("Check passphrase and try again", self.task.message)

        # Run task with the correct passphrase
        self.run_task("cla")
        self.assertEqual("", self.task.message)
