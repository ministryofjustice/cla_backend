import time
from django.core.management import BaseCommand
from django.conf import settings
from legalaid.utils import diversity
from core.tests.mommy_utils import make_recipe


class Command(BaseCommand):
    help = "Create dummy personal data"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stderr("This command can only run in DEBUG MODE")
            return

        if settings.CLA_ENV not in ["local", "uat", "staging"]:
            self.stderr("This command can only run on the following environments: local, uat and staging")
            return
        maximum = 60000
        self.stdout.write("THIS COMMAND WILL CREATING {} DUMMY CASES/PERSONAL DETAILS RECORD".format(maximum))
        reply = raw_input("ARE YOU SURE YOU WANT TO DO THIS(YES/NO): ")
        if reply != "YES":
            self.stdout.write("You did not answer YES, process aborted")
            return

        counter = 1
        data = {
            'gender': 'Prefer not to say',
            'religion': 'Prefer not to say',
            'disability': 'PNS - Prefer not to say',
            'ethnicity': 'Prefer not to say',
            'sexual_orientation': 'Prefer Not To Say'
        }
        start = time.time()
        while counter <= maximum:
            self.stdout.write("Creating personal data {}".format(counter))
            pd = make_recipe("legalaid.personal_details", postcode="SW1AA", street="Petty France")
            diversity.save_diversity_data(pd.pk, data)
            print(diversity.load_diversity_data(pd.pk, "cla"))
            counter += 1

        duration = time.time() - start
        print "It took {} seconds to create {} personal data records".format(duration, maximum)
