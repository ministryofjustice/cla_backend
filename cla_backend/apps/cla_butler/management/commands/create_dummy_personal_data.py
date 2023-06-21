import time
from django.core.management import BaseCommand
from django.conf import settings
from legalaid.utils import diversity
from core.tests.mommy_utils import make_recipe


class Command(BaseCommand):
    help = "Create dummy personal data"

    def handle(self, counter, **options):
        counter = int(counter)
        if not settings.DEBUG:
            self.stderr("This command can only run in DEBUG MODE")
            return

        if settings.CLA_ENV not in ["local", "uat", "staging"]:
            self.stderr("This command can only run on the following environments: local, uat and staging")
            return
        self.stdout.write("THIS COMMAND WILL CREATING {} DUMMY CASES/PERSONAL DETAILS RECORD".format(counter))
        reply = raw_input("ARE YOU SURE YOU WANT TO DO THIS(YES/NO): ")
        if reply != "YES":
            self.stdout.write("You did not answer YES, process aborted")
            return

        data = {
            "gender": "Prefer not to say",
            "religion": "Prefer not to say",
            "disability": "PNS - Prefer not to say",
            "ethnicity": "Prefer not to say",
            "sexual_orientation": "Prefer Not To Say",
        }
        start = time.time()
        index = 1
        while index <= counter:
            self.stdout.write("Creating personal data {}".format(index))
            pd = make_recipe("legalaid.personal_details", postcode="SW1AA", street="Petty France")
            diversity.save_diversity_data(pd.pk, data)
            index += 1

        duration = time.time() - start
        self.stdout.write("It took {} seconds to create {} personal data records".format(duration, counter))
