import contextlib
import boto
import os
import json
import shutil
import time
from contextlib import closing
from django.contrib.auth.models import User
import csvkit as csv

from celery import Task
from django.core.exceptions import ImproperlyConfigured
from django.db import InternalError
from django.utils.six import text_type
from dateutil.relativedelta import relativedelta
from django.conf import settings

from .utils import OBIEEExporter
from .models import Export
from .constants import EXPORT_STATUS


@contextlib.contextmanager
def csv_writer(csv_file):
    yield csv.writer(csv_file)


def import_form(class_name):
    mod = __import__('reports.forms', fromlist=[class_name])
    return getattr(mod, class_name)


class ExportTaskBase(Task):
    def __init__(self):
        self.filepath = ''
        self.message = ''
        self.export = None
        self.form = None
        self.user = None

    def _create_export(self):
        self.export = Export.objects.create(
            user=self.user,
            task_id=self.request.id,
            status=EXPORT_STATUS.started,
        )

    def _set_up_form(self, form_class_name, post_data):
        form_class = import_form(form_class_name)
        self.form = form_class()
        self.form.data = json.loads(post_data)
        self.form.is_bound = True
        if not self.form.is_valid():
            self.message = u'The form submitted was not valid'
            raise Exception(self.message)

    def _filepath(self, filename):
        file_name, file_ext = os.path.splitext(filename)
        user_datetime = '%s-%s' % (self.user.pk, time.strftime("%Y-%m-%d-%H%M%S"))
        filename = '%s-%s%s' % (file_name, user_datetime, file_ext)
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
        conn = boto.connect_s3(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.lookup(settings.AWS_STORAGE_BUCKET_NAME)
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
            csv_data = list(self.form)
            csv_file = open(self.filepath, 'w')
            with csv_writer(csv_file) as writer:
                map(writer.writerow, csv_data)
            csv_file.close()
            self.send_to_s3()
        except InternalError as error:
            error_message = text_type(error).strip()
            if 'wrong key' in error_message.lower() or 'corrupt data' in \
                    error_message.lower():
                # e.g. if pgcrypto key is incorrect
                self.message = u'Check passphrase and try again'
            else:
                self.message = u'An error occurred:\n%s' % error_message


class OBIEEExportTask(ExportTaskBase):
    def run(self, user_id, filename, form_class_name, post_data, *args, **kwargs):
        """
        Export a full dump of the db for OBIEE export and make it available
        for downloads
        """
        self.user = User.objects.get(pk=user_id)
        self._create_export()
        self._set_up_form(form_class_name, post_data)

        diversity_keyphrase = self.form.cleaned_data['passphrase']
        start = self.form.month
        end = self.form.month + relativedelta(months=1)
        if not settings.OBIEE_ZIP_PASSWORD:
            raise ImproperlyConfigured('OBIEE Zip password must be set.')

        self.filepath = self._filepath(filename)
        with closing(OBIEEExporter(settings.TEMP_DIR, diversity_keyphrase,
                start, end, filename=os.path.basename(self._filepath(filename)))) as exporter:
            try:
                self.filepath = exporter.export()
                self.send_to_s3()
            except Exception:
                self.message = u'An error occurred creating the zip file'
                raise
            finally:
                pass
