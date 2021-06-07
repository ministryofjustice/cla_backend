from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils import timezone

from legalaid.models import Case


class Command(BaseCommand):
    help = "Recalculate case.assigned_out_of_hours since a given date"

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

        self.stdout.write("{count} cases assigned since {dt}.".format(count=count, dt=dt))
        if not count:
            return

        unchanged = []
        changed_to_true = []
        changed_to_false = []

        for case in cases:
            current_value = case.assigned_out_of_hours
            new_value = self.recalculate_field(case)
            if new_value == current_value:
                unchanged.append(case.pk)
            elif new_value:
                changed_to_true.append(case.pk)
            else:
                changed_to_false.append(case.pk)

        self.stdout.write("{count} cases already had the correct value.".format(count=len(unchanged)))
        self.stdout.write("{count} cases will be changed to `True`.".format(count=len(changed_to_true)))
        self.stdout.write("{count} cases will be changed to `False`.".format(count=len(changed_to_false)))

    def recalculate_field(self, case):
        case_category = getattr(case.eligibility_check.category, "code") if case.eligibility_check else None
        non_rota_hours = settings.NON_ROTA_OPENING_HOURS[case_category]
        return not non_rota_hours.available(case.provider_assigned_at, tz_aware=True)
