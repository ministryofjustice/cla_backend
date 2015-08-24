import contextlib
import csv
import os
import sys

from django.core.management.base import BaseCommand

from ._media_codes import MediaCodeList

FIXTURE_PATH = 'cla_backend/apps/legalaid/fixtures/media_codes.json'


@contextlib.contextmanager
def csv_data(path):
    with contextlib.closing(open(path, 'rU')) as csv_file:
        yield csv.reader(csv_file)


def fixture_filehandle():
    return contextlib.closing(open(FIXTURE_PATH, 'w'))


def readable(path):
    return os.access(path, os.R_OK)


class Command(BaseCommand):
    args = 'CSV_FILE.csv'
    help = ('Converts a CSV spreadsheet of media codes into a fixture ready '
            'to be loaddata\'d into the database')

    def handle(self, *args, **kwargs):
        path = args[0] if args else None

        if not path:
            self.die('Path to the media codes CSV file is required', 1)

        if not readable(path):
            self.die('File {0} could not be read'.format(path), 2)

        with csv_data(path) as rows:
            media_codes = MediaCodeList(rows)

        with fixture_filehandle() as fixture:
            fixture.write(media_codes.as_json())

    def die(self, msg, code):
        self.stderr.write(msg)
        sys.exit(code)
