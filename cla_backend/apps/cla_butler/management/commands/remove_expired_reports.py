# coding=utf-8
import logging
from django.core.management.base import BaseCommand
from reports.models import Export
from django.utils import timezone
from dateutil.relativedelta import relativedelta


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Removes all extract reports that were created over 2 years ago."

    def handle(self, *args, **options):
        self.remove_expired_reports()

    @staticmethod
    def remove_expired_reports():
        for report in Export.objects.filter(created__lte=timezone.now() - relativedelta(years=2)):
            report.delete()
