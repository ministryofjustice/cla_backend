# coding=utf-8
import logging
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "This runs the MCCB1sSLA report"

    def handle(self, *args, **options):
        self.create_report()

    def create_report():
        print("stuff goes here")

        # '{"action": "Export", "csrfmiddlewaretoken": "PQk4Pt55CL0NBapx9hSqZTJkSn6tL6TL", "date_from": "08/05/2021", "date_to": "10/05/2021"}'

        # report_data = json_stuff_goes_here
        #         ExportTask().delay(user_person.pk, filename_of_report, mi_cb1_extract_agilisys, report_data)
