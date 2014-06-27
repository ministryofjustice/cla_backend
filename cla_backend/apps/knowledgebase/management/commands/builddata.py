""""
usage-
./manage.py builddata load_knowledgebase_csv ~/Documents/Scratch/knowledgebase.csv

Creates derived dataset of constants used by JS frontend. Data is sourced from cla_common.

"""
from django.core.management.base import BaseCommand
import os
import sys
from pprint import pprint
from ._csv_2_fixture import KnowledgebaseCsvParse

class Command(BaseCommand):
    args = 'load_knowledgebase_csv CSV_FILE.csv'
    help = ( 'Create a derived dataset. At present, just load_knowledgebase_csv '
             'is implemented. It loads a CSV spreadsheet into a fixture ready '
             'to be loaddata\'ed into DB'
            )
    
    KNOWLEDGEBASE_FIXTURE = 'cla_backend/apps/knowledgebase/fixtures/kb_from_spreadsheet.json'

    def handle(self, *args, **options):

        if args[0] == 'load_knowledgebase_csv':
            
            if len(args) != 2:
                self.stdout.write("Last argument needs to be path to CSV file")
                sys.exit(-1)
            if not os.access(args[1], os.R_OK):
                self.stdout.write("File '%s' couldn't be read" % args[1])
                sys.exit(-1)

            # read in CSV and feed to fixture builder
            f_in = open(args[1], "rU")
            c = KnowledgebaseCsvParse(f_in)
            json = c.fixture_as_json()
            f_in.close()

            # write json doc to fixture file
            f_out = open(self.KNOWLEDGEBASE_FIXTURE, "w")
            f_out.write(json)
            f_out.close()

            self.stdout.write("Fixture written to %s" % self.KNOWLEDGEBASE_FIXTURE)
            