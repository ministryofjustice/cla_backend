import sys
from django.core.management.base import BaseCommand
from dateutil.relativedelta import relativedelta

from legalaid.models import Case
from cla_butler.tasks import DeleteOldData


class FindAndDeleteCasesUsingCreationTime(DeleteOldData):
    def get_eligible_cases(self):
        two_years = self.now - relativedelta(years=2)

        return Case.objects.filter(created__lte=two_years).exclude(log__created__gte=two_years)


class Command(BaseCommand):
    help = (
        "Find or delete cases that are 2 years old or over that were not deleted prior to the task command being fixed"
    )

    def handle(self, *args, **kwargs):
        instance = FindAndDeleteCasesUsingCreationTime()
        cases = instance.get_eligible_cases()
        if len(args) and args[0] == "delete":
            if len(args) > 1 and args[1] == "no-input":
                instance.run()
            elif sys.argv[1] == "test":
                instance.run()
            else:
                answer = raw_input(
                    "Number of cases that will be deleted: "
                    + str(cases.count())
                    + "\nAre you sure about this? (Yes/No) "
                )
                if answer == "Yes":
                    instance.run()
        elif sys.argv[1] == "test":
            return cases
        else:
            print("Number of cases to be deleted: " + str(cases.count()))
