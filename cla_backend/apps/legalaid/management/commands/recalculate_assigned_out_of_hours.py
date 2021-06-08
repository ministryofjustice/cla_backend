from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils import timezone

from legalaid.models import Case


class Command(BaseCommand):
    help = "Recalculate case.assigned_out_of_hours since a given date"

    unchanged = []
    change_to_true = []
    change_to_false = []

    def handle(self, *args, **options):
        try:
            date_string = args[0]
        except IndexError:
            raise CommandError("A start date is required")

        try:
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
            commit = args[1] == "commit"
        except IndexError:
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
