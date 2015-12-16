import contextlib
import shutil
import tempfile
from contextlib import closing
import csv

from celery import shared_task
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


@shared_task(bind=True)
# def obiee_export(self, diversity_keyphrase, dt_from, dt_to):
def obiee_export(self, filename, form):
    """
    Export a full dump of the db for OBIEE export and make it available for
    downloads
    """
    diversity_keyphrase = form.cleaned_data['passphrase']
    start = form.month
    end = form.month + relativedelta(months=1)
    if not settings.OBIEE_ZIP_PASSWORD:
        raise ImproperlyConfigured('OBIEE Zip password must be set.')
    obiee_export.delay(diversity_keyphrase, start, end)

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


@contextlib.contextmanager
def csv_writer(csv_file):
    yield csv.writer(csv_file)


@shared_task
def create_export(filename, form):
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

