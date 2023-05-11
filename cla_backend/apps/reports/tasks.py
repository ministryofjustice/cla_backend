import contextlib
import os
import json
import shutil
import time
import glob
import pyminizip
import tempfile
from contextlib import closing
from django.contrib.auth.models import User
import csvkit as csv
import logging

from celery import Task
from django.core.exceptions import ImproperlyConfigured
from django.db import InternalError
from django.utils.six import text_type
from dateutil.relativedelta import relativedelta
from django.conf import settings

from .utils import OBIEEExporter, get_s3_connection
from .models import Export
from .constants import EXPORT_STATUS
from core.utils import remember_cwd
from checker.models import ReasonForContacting
from urlparse import urlparse

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def csv_writer(csv_file):
    yield csv.writer(csv_file)


def import_form(class_name):
    mod = __import__("reports.forms", fromlist=[class_name])
    return getattr(mod, class_name)


class ExportTaskBase(Task):
    def __init__(self):
        self.filepath = ""
        self.message = ""
        self.export = None
        self.form = None
        self.user = None

    def _create_export(self):
        self.export = Export.objects.create(user=self.user, task_id=self.request.id, status=EXPORT_STATUS.started)

    def _set_up_form(self, form_class_name, post_data):
        form_class = import_form(form_class_name)
        self.form = form_class()
        self.form.data = json.loads(post_data)
        self.form.is_bound = True
        if not self.form.is_valid():
            self.message = u"The form submitted was not valid"
            raise Exception(self.message)

    def _filepath(self, filename):
        file_name, file_ext = os.path.splitext(filename)
        user_datetime = "%s-%s" % (self.user.pk, time.strftime("%Y-%m-%d-%H%M%S"))
        filename = "%s-%s%s" % (file_name, user_datetime, file_ext)
        return os.path.join(settings.TEMP_DIR, filename)

    def on_success(self, retval, task_id, args, kwargs):
        self.export.status = EXPORT_STATUS.created
        self.export.path = self.filepath
        self.export.message = self.message
        self.export.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.export.status = EXPORT_STATUS.failed
        self.export.message = self.message
        self.export.save()

    def send_to_s3(self):
        conn = get_s3_connection()
        try:
            bucket = conn.get_bucket(settings.AWS_REPORTS_STORAGE_BUCKET_NAME)
        except Exception as e:
            logger.error(
                "Reports bucket couldn't be fetched. Ensure s3 credentials set. You may need the S3_USE_SIGV4 env var"
            )
            raise e
        k = bucket.new_key(settings.EXPORT_DIR + os.path.basename(self.filepath))
        k.set_contents_from_filename(self.filepath)
        shutil.rmtree(self.filepath, ignore_errors=True)


class ExportTask(ExportTaskBase):
    def run(self, user_id, filename, form_class_name, post_data, *args, **kwargs):
        self.user = User.objects.get(pk=user_id)
        self._create_export()
        self._set_up_form(form_class_name, post_data)

        self.filepath = self._filepath(filename)
        try:
            csv_data = self.form.get_output()
            csv_file = open(self.filepath, "w")
            with csv_writer(csv_file) as writer:
                map(writer.writerow, csv_data)
            csv_file.close()
            # check if there is a connection to aws, otherwise don't try to save
            if settings.AWS_REPORTS_STORAGE_BUCKET_NAME:
                self.send_to_s3()
        except InternalError as error:
            error_message = text_type(error).strip()
            if "wrong key" in error_message.lower() or "corrupt data" in error_message.lower():
                # e.g. if pgcrypto key is incorrect
                self.message = u"Check passphrase and try again"
            else:
                self.message = u"An error occurred:\n%s" % error_message


class OBIEEExportTask(ExportTaskBase):
    def run(self, user_id, filename, form_class_name, post_data, *args, **kwargs):
        """
        Export a full dump of the db for OBIEE export and make it available
        for downloads
        """
        self.user = User.objects.get(pk=user_id)
        self._create_export()
        self._set_up_form(form_class_name, post_data)
        # A task is not instantiated for every request. So unless we reset this message it will contain incorrect value
        # https://docs.celeryproject.org/en/3.0/userguide/tasks.html#instantiation
        self.message = ""

        diversity_keyphrase = self.form.cleaned_data["passphrase"]
        start = self.form.month
        end = self.form.month + relativedelta(months=1)
        if not settings.OBIEE_ZIP_PASSWORD:
            raise ImproperlyConfigured("OBIEE Zip password must be set.")

        self.filepath = self._filepath(filename)
        with closing(
            OBIEEExporter(
                settings.TEMP_DIR, diversity_keyphrase, start, end, filename=os.path.basename(self._filepath(filename))
            )
        ) as exporter:
            try:
                self.filepath = exporter.export()
                self.send_to_s3()
            except Exception as e:
                message = getattr(e, "message", "") or getattr(e, "strerror", "")
                message = text_type(message).strip()
                if "wrong key" in message.lower() or "corrupt data" in message.lower():
                    # e.g. if pgcrypto key is incorrect
                    self.message = u"Check passphrase and try again"
                else:
                    self.message = u"An error occurred creating the zip file: {message}".format(message=message)
                raise
            finally:
                pass


class ReasonForContactingExportTask(ExportTaskBase):
    def run(self, user_id, filename, form_class_name, post_data, *args, **kwargs):
        """
        Export csv files for each of the referrers from reason for contacting
        """
        self.user = User.objects.get(pk=user_id)
        self._create_export()
        self._set_up_form(form_class_name, post_data)
        # A task is not instantiated for every request. So unless we reset this message it will contain incorrect value
        # https://docs.celeryproject.org/en/3.0/userguide/tasks.html#instantiation
        self.message = ""
        # zip_filepath = self._filepath(filename)
        # pone file that does everything
        # ----------
        # loop through the referrers
        for referrer in ReasonForContacting.get_top_referrers():
            #   get the results we want
            self.export_csv(referrer["referrer"])
        self.generate_zip()
        self.send_to_s3()

    def export_csv(self, referrer_url):
        try:
            self.form.top_referrer = urlparse(referrer_url)[2]
            url_relative_path = urlparse(referrer_url)[2].replace("/", "_").strip("_")
            file_name = ".".join(["".join(["rfc_", url_relative_path]), "csv"])
            csv_data = self.form.get_output()
            csv_file = open(self.full_path(file_name), "w")
            with csv_writer(csv_file) as writer:
                map(writer.writerow, csv_data)
            csv_file.close()
        except InternalError as error:
            self.message = error
            raise

    def full_path(self, file_name):
        return os.path.join(settings.TEMP_DIR, file_name)

    def generate_zip(self):
        tmp_export_path = tempfile.mkdtemp()
        with remember_cwd():
            try:
                os.chdir(tmp_export_path)
                pyminizip.compress_multiple(glob.glob("*.csv"), [], self.filename, "password", 9)
                shutil.move("%s/%s" % (tmp_export_path, self.filename), "%s/%s" % (settings.TEMP_DIR, self.filename))
            finally:
                shutil.rmtree(tmp_export_path)
