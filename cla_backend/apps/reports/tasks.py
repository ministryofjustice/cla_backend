import contextlib
import shutil
import tempfile
from contextlib import closing
import csvkit as csv

from celery import Task
from django.core.exceptions import ImproperlyConfigured
from django.db import InternalError
from django.utils.six import text_type
from dateutil.relativedelta import relativedelta
from django.conf import settings

from .utils import OBIEEExporter
from .models import Export


def create_export_ref():
    export = Export.objects.create(

    )


@contextlib.contextmanager
def csv_writer(csv_file):
    yield csv.writer(csv_file)


class ExportTask(Task):
    def run(self, filename, form):
        outfile_path = '%s' %(filename)
        try:
            csv_data = list(form)
            with csv_writer(open(outfile_path, 'w')) as writer:
                map(writer.writerow, csv_data)
        except InternalError as error:
            error_message = text_type(error).strip()
            if 'wrong key' in error_message.lower() or 'corrupt data' in error_message.lower():
                # e.g. if pgcrypto key is incorrect
                error_message = 'Check passphrase and try again'
            else:
                error_message = u'An error occurred:\n%s' % error_message

    def on_success(self, retval, task_id, args, kwargs):
        pass

    def on_failure(self, retval, task_id, args, kwargs):
        pass


class OBIEEExportTask(ExportTask):
    def run(self, filename, form):
        """
        Export a full dump of the db for OBIEE export and make it available for
        downloads
        """
        diversity_keyphrase = form.cleaned_data['passphrase']
        start = form.month
        end = form.month + relativedelta(months=1)
        if not settings.OBIEE_ZIP_PASSWORD:
            raise ImproperlyConfigured('OBIEE Zip password must be set.')
        filename = 'cla_database.zip'

        temp_path = tempfile.mkdtemp(suffix=self.request.id)
        with closing(OBIEEExporter(temp_path, diversity_keyphrase,
                      start, end, filename=filename)) as exporter:
            try:
                zip_path = exporter.export()
            except Exception:
                raise
            finally:
                shutil.rmtree(temp_path, ignore_errors=True)

