# coding=utf-8
import logging
from datetime import date, timedelta
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
        date_from = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_to = date.today().strftime("%Y-%m-%d")

        report_data = '{{"action": "Export", "csrfmiddlewaretoken": "PQk4Pt55CL0NBapx9hSqZTJkSn6tL6TL", "date_from": "{0}", "date_to": "{1}"}}'.format(
            date_from, date_to
        )

        web_user = get_web_user()
        filename_of_report = "scheduled-mi-cb1-extract.csv"
        ExportTask().delay(web_user.pk, filename_of_report, "MICB1Extract", report_data)
