# coding=utf-8
import logging
from django.core.management.base import BaseCommand


from cla_eventlog.constants import LOG_LEVELS, LOG_TYPES
from cla_eventlog.models import Log


MAX_REPORT_AGE_DAYS = 730

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Removes all reports from the db and S3 Buckets that are 2 years old or greater."

    def handle(self, *args, **options):
        self.remove_expired_reports()

    @staticmethod
    def remove_expired_reports():
        
        logger.info("")
