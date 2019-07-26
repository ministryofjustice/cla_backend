from django.core.management import BaseCommand
from call_centre.models import Organisation, Operator


class Command(BaseCommand):
    help = "Create Agilisys organisation and assign current agilisys operators to that organisation"

    def handle(self, *args, **options):
        (organisation, created) = Organisation.objects.get_or_create(name="Agilisys")
        operators = Operator.objects.filter(organisation__isnull=True, user__email__endswith="@agilisys.co.uk")
        if not operators.count():
            self.stdout.write("Could not find Agilisys operators to update")
        else:
            self.stdout.write("Updating {count} Agilisys operators...".format(count=operators.count()), ending="")
            operators.update(organisation=organisation)
            self.stdout.write("done")
