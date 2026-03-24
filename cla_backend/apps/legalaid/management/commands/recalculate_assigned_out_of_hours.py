from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils import timezone
from argparse import SUPPRESS
from legalaid.models import Case


class Command(BaseCommand):
    help = "Recalculate case.assigned_out_of_hours since a given date"

    def __init__(self, *args, **kwargs):
        self.unchanged = []
        self.change_to_true = []
        self.change_to_false = []
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("date_string", nargs="?", default=SUPPRESS)
        parser.add_argument("commit", nargs="?", default=SUPPRESS)

    def handle(self, *args, **options):
        if "date_string" not in options:
            raise CommandError("A start date is required")
        try:
            date_string = options["date_string"]
            dt = timezone.datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            raise CommandError("The start date should be a valid datetime in yyyy-mm-dd format")

        cases = Case.objects.filter(provider_assigned_at__gte=dt)
        count = cases.count()

        self.stdout.write(u"{count} cases assigned since {dt}.".format(count=count, dt=dt))
        if not count:
            return

        self.group_cases(cases)

        self.stdout.write(u"{count} cases already had the correct value.".format(count=len(self.unchanged)))
        self.stdout.write(u"{count} cases will be changed to `True`.".format(count=len(self.change_to_true)))
        self.stdout.write(u"{count} cases will be changed to `False`.".format(count=len(self.change_to_false)))

        try:
            commit = options["commit"] == "commit"
        except KeyError:
            commit = False

        if commit:
            number_changed_to_true = Case.objects.filter(pk__in=self.change_to_true).update(assigned_out_of_hours=True)
            number_changed_to_false = Case.objects.filter(pk__in=self.change_to_false).update(
                assigned_out_of_hours=False
            )
            self.stdout.write(u"Making changes")
            self.stdout.write(u"  {count} cases changed to `True`.".format(count=number_changed_to_true))
            self.stdout.write(u"  {count} cases changed to `False`.".format(count=number_changed_to_false))
        else:
            self.stdout.write(u"Not making changes (add 'commit' to make changes)")

    def group_cases(self, cases):
        for case in cases:
            current_value = case.assigned_out_of_hours
            new_value = self.recalculate_field(case)
            if new_value == current_value:
                self.unchanged.append(case.pk)
            elif new_value:
                self.change_to_true.append(case.pk)
            else:
                self.change_to_false.append(case.pk)

    def recalculate_field(self, case):
        case_category = getattr(case.eligibility_check.category, "code") if case.eligibility_check else None
        non_rota_hours = settings.NON_ROTA_OPENING_HOURS[case_category]
        return not non_rota_hours.available(case.provider_assigned_at, tz_aware=True)
