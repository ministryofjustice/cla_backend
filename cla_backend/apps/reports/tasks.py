import contextlib
import os
import json
import shutil
import time
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
        # this creates a unique filepath for each report
        # uniqueness is from user pk and datetime
        # file will be in settings.TEMP_DIR
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
        self.tmp_export_path = tempfile.mkdtemp()
        self.user = User.objects.get(pk=user_id)
        self._create_export()
        self._set_up_form(form_class_name, post_data)
        # A task is not instantiated for every request. So unless we reset this message it will contain incorrect value
        # https://docs.celeryproject.org/en/3.0/userguide/tasks.html#instantiation
        self.message = ""
        # this is the filepath that will be used to send to aws bucket/displayed on report page
        self.filepath = self._filepath(filename)
        # make the files and then put them in zip and delete temp folder
        try:
            # first file that contains all reasons for contacting
            self.export_rfc_csv()
            # loop through each individual referrer file
            for referrer in ReasonForContacting.get_top_referrers():
                #   get the results for that individual stage in the journey
                referrer_url = referrer["referrer"]
                self.form.referrer = urlparse(referrer_url)[2]
                self.export_rfc_csv(referrer_url)
            self.generate_rfc_zip()
            if settings.AWS_REPORTS_STORAGE_BUCKET_NAME:
                self.send_to_s3()
        except Exception as e:
            message = getattr(e, "message", "") or getattr(e, "strerror", "")
            message = text_type(message).strip()
            self.message = u"An error occurred creating the zip file: {message}".format(message=message)
            raise
        finally:
            pass

    def export_rfc_csv(self, referrer_url=None):
        try:
            csv_data = self.form.get_output()
            csv_file = open(self.full_csv_filepath(referrer_url), "w")
            with csv_writer(csv_file) as writer:
                map(writer.writerow, csv_data)
            csv_file.close()
        except InternalError as error:
            self.message = error
            raise

    def full_csv_filepath(self, referrer_url=None):
        # create a unique filepath for csv
        user_datetime = "%s-%s" % (self.user.pk, time.strftime("%Y-%m-%d-%H%M%S"))
        file_ext = ".csv"
        if referrer_url is not None:
            # this is the csv for one referrer
            self.form.top_referrer = urlparse(referrer_url)[2]
            url_relative_path = urlparse(referrer_url)[2].replace("/", "_").strip("_")
            file_name = "%s-%s%s" % ("".join(["rfc_", url_relative_path]), user_datetime, file_ext)
        else:
            # this is the csv with all the results
            file_name = "%s-%s%s" % ("rfc_all_referrers", user_datetime, file_ext)
        return os.path.join(self.tmp_export_path, file_name)

    def generate_rfc_zip(self):
        tmp_export_path = tempfile.mkdtemp()
        with remember_cwd():
            try:
                os.chdir(self.tmp_export_path)
                zip_filepath = os.path.join(tmp_export_path, "temp_rfc_zip")
                zip_created = shutil.make_archive(base_name=zip_filepath, format="zip", root_dir=self.tmp_export_path)
                shutil.move(zip_created, self.filepath)
            finally:
                shutil.rmtree(tmp_export_path)
                shutil.rmtree(self.tmp_export_path)
