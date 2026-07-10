""" "
usage-
./manage.py builddata load_knowledgebase_csv ~/Documents/Scratch/knowledgebase.csv

Creates derived dataset of constants used by JS frontend. Data is sourced from cla_common.

you can then load the fixture with-
./manage.py loaddata cla_backend/apps/knowledgebase/fixtures/kb_from_spreadsheet.json

"""

from django.core.management.base import BaseCommand
import os
import sys
from ._csv_2_fixture import KnowledgebaseCsvParse


class Command(BaseCommand):
    help = (
        "Create a derived dataset. At present, just load_knowledgebase_csv "
        "is implemented. It loads a CSV spreadsheet into a fixture ready "
        "to be loaddata'ed into DB"
    )

    KNOWLEDGEBASE_FIXTURE = "cla_backend/apps/knowledgebase/fixtures/kb_from_spreadsheet.json"

    def add_arguments(self, parser):
        parser.add_argument("action")
        parser.add_argument("csv_file")

    def handle(self, *args, **options):

        action = options["action"]
        csv_file = options["csv_file"]

        if action == "load_knowledgebase_csv":

            if not os.access(csv_file, os.R_OK):
                self.stdout.write("File '%s' couldn't be read" % csv_file)
                sys.exit(-1)

            # read in CSV and feed to fixture builder
            f_in = open(csv_file, "r")
            c = KnowledgebaseCsvParse(f_in)
            json = c.fixture_as_json()
            f_in.close()

            # write json doc to fixture file
            f_out = open(self.KNOWLEDGEBASE_FIXTURE, "w")
            f_out.write(json)
            f_out.close()

            self.stdout.write("Fixture written to %s" % self.KNOWLEDGEBASE_FIXTURE)
