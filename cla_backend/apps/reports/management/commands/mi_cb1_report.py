# coding=utf-8
import logging
from django.core.management.base import BaseCommand
from reports.tasks import ExportTask
from core.models import get_web_user
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "This runs the MCCB1sSLA report"

    def handle(self, *args, **options):
        self.create_report()

    @csrf_exempt
    def create_report(self):
        report_data = '{"action": "Export", "csrfmiddlewaretoken": "PQk4Pt55CL0NBapx9hSqZTJkSn6tL6TL", "date_from": "2021-05-08", "date_to": "2021-05-10"}'

        web_user = get_web_user()
        filename_of_report = "WEEKLY-REPORT-TEST.csv"
        ExportTask().delay(web_user.pk, filename_of_report, "MICB1Extract", report_data)
