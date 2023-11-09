# coding=utf-8
import logging
from django.core.management.base import BaseCommand

from reports.models import Export


MAX_REPORT_AGE_DAYS = 730

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Removes all reports from the db and S3 Buckets that are 2 years old or greater."

    def handle(self, *args, **options):
        self.remove_expired_reports()


    @staticmethod
    def remove_expired_reports():

        # Loop through local database to get m1 report name / time.
        for report in Export.objects.all():
            print(report.path)
        # Take name / time and search s3 bucket to see if it exists.
        # If yes:
            # Check age:
                # If old than two years old: Delete
        # If no:
            # Clean up
        
