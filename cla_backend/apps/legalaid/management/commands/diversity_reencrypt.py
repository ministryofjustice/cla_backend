import os
from django.core.management import BaseCommand
from legalaid.utils import diversity
from legalaid.models import PersonalDetails


class Command(BaseCommand):
    help = "Re-encrypt diversity data"

    def handle(self, *args, **options):
        key = os.environ.get("PREVIOUS_DIVERSITY_PRIVATE_KEY", None)
        if not key:
            self.stderr.write("Could not find environment variable PREVIOUS_DIVERSITY_PRIVATE_KEY")
            return
        passphrase = raw_input("Please enter the passphrase for the PREVIOUS private key:")
        diversity.reencrypt(diversity._format_env_key(key), passphrase)
        self.stdout.write("Re-encrypting of diversity data has been completed.")

        passphrase = raw_input("Please enter the passphrase for the CURRENT NEW private key:")

        self.stdout.write("Checking we can decode the FIRST diversity record.")
        pd = PersonalDetails.objects.filter(diversity__isnull=False).all().last()
        diversity_data = diversity.load_diversity_data(pd.pk, passphrase)
        self.stdout.write(str(diversity_data))

        self.stdout.write("Checking we can decode the LAST diversity record.")
        pd = PersonalDetails.objects.filter(diversity__isnull=False).all().first()
        diversity_data = diversity.load_diversity_data(pd.pk, passphrase)
        self.stdout.write(str(diversity_data))
