import os
from django.core.management.base import BaseCommand
from cla_butler.tasks import DiversityDataReencryptTask
from cla_butler.models import DiversityDataCheck, ACTION


class Command(BaseCommand):
    help = "Re-encrypt diversity data"

    def handle(self, *args, **options):
        previous_key = os.environ.get("PREVIOUS_DIVERSITY_PRIVATE_KEY", None)
        if not previous_key:
            self.stderr.write("Could not find environment variable PREVIOUS_DIVERSITY_PRIVATE_KEY")
            return
        passphrase_old = self.get_old_key_passphrase()

        qs = DiversityDataCheck.get_unprocessed_personal_data_qs(ACTION.REENCRYPT)
        self.stdout.write("Personal data with diversity not null is: {}".format(qs.count()))
        self.schedule_tasks(qs, 1000, passphrase_old, previous_key)

    def schedule_tasks(self, qs, chunk_size, passphrase_old, previous_key):
        total_records = qs.count()
        counter = 1
        for start in range(0, total_records, chunk_size):
            end = start + chunk_size
            description = "{index} - {start}:{end}".format(index=counter, start=start, end=end)
            self.stdout.write(description)
            DiversityDataReencryptTask().delay(passphrase_old, previous_key, start, end, description)
            counter += 1

    def get_old_key_passphrase(self):
        return raw_input("Please enter the passphrase for the PREVIOUS private key:")
