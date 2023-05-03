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
        self.schedule_tasks(qs, 1000, passphrase_old)

    def schedule_tasks(self, qs, chunk_size, passphrase_old):
        total_records = qs.count()
        tasks = []
        for start in range(0, total_records, chunk_size):
            end = start + chunk_size
            tasks.append(qs[start:end].values_list("id", flat=True))
        self.stdout.write("Processing the number of tasks: {}".format(len(tasks)))

        for ids in tasks:
            DiversityDataReencryptTask().delay(passphrase_old, list(ids))

    def get_old_key_passphrase(self):
        return raw_input("Please enter the passphrase for the PREVIOUS private key:")