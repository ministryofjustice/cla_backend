from django.core.management.base import BaseCommand
from dateutil.relativedelta import relativedelta

from legalaid.models import Case
from cla_butler.tasks import DeleteOldData
from cla_eventlog.models import Log


class FindAndDeleteCasesUsingCreationTime(DeleteOldData):
    def get_eligible_cases(self):
        two_years = self.now - relativedelta(years=2)
        old_cases = []

        filtered_cases = Case.objects.filter(created__lte=two_years)
        for case in filtered_cases:
            try:
                latest_log = Log.objects.filter(case__id=case.id).latest("created")
                if latest_log.created <= two_years:
                    old_cases.append(case.id)
            except Log.DoesNotExist:
                # Old case without any event logs
                old_cases.append(case.id)

        return Case.objects.filter(id__in=old_cases)


class Command(BaseCommand):
    help = "Find and delete cases that are 2 years old or over that were not deleted prior to the task command being fixed"

    def handle(self, *args, **kwargs):
        FindAndDeleteCasesUsingCreationTime().run()
