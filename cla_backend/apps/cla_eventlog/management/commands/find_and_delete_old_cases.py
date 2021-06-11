import sys
from django.core.management.base import BaseCommand
from dateutil.relativedelta import relativedelta

from legalaid.models import Case
from cla_eventlog.models import Log
from cla_butler.tasks import DeleteOldData


class FindAndDeleteCasesUsingCreationTime(DeleteOldData):
    def get_eligible_cases(self):
        two_years = self.now - relativedelta(years=2)

        return Case.objects.filter(created__lte=two_years).exclude(log__created__gte=two_years)

    def get_digital_justice_user_logs(self):
        return Log.objects.filter(created_by__email__endswith="digital.justice.gov.uk")


class Command(BaseCommand):
    help = """
        Use cases:
        1. Find or delete cases that are 2 years old or over that were not deleted prior to the task command being fixed
        2. Delete logs created by users with a @digital.justice.gov.uk email
        """

    def get_user_input(self, qs_type, qs):
        return raw_input(
            "Number of {0} that will be deleted: {1}\nAre you sure about this? (Yes/No) ".format(
                qs_type, qs.count()
            )
        )

    def handle_test_command(self, args, cases):
        if args[0] == "delete":
            self.instance.run()
        elif args[0] == "delete-logs":
            digital_justice_user_logs = self.instance.get_digital_justice_user_logs()
            self.instance._delete_objects(digital_justice_user_logs)

    def handle_terminal_command(self, args, cases):
        if args[0] == "delete":
            if len(args) > 1 and args[1] == "no-input":
                self.instance.run()
            else:
                answer = get_user_input("cases", cases)
                if answer == "Yes":
                    self.instance.run()
        elif args[0] == "delete-logs":
            digital_justice_user_logs = self.instance.get_digital_justice_user_logs()
            answer = get_user_input("digital justice user logs", digital_justice_user_logs)
            if answer == "Yes":
                self.instance._delete_objects(digital_justice_user_logs)

    def handle(self, *args, **kwargs):
        self.instance = FindAndDeleteCasesUsingCreationTime()
        cases = self.instance.get_eligible_cases()
        django_command = sys.argv[1]

        if django_command == "test":  # If command is run in test
            if args:
                self.handle_test_command(args, cases)
            else:
                return cases
        else:  # If command is run in terminal
            if args:
                self.handle_terminal_command(args, cases)
            else:
                print("Number of cases to be deleted: " + str(cases.count()))
