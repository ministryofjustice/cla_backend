import os
from django.core.management.base import BaseCommand
from cla_butler.tasks import DiversityDataReencryptTask
from cla_butler.models import DiversityDataCheck, ACTION


class Command(BaseCommand):
    help = "Re-encrypt diversity data"
    # Number of records processed by each celery task
    chunk_size = 1000

    def handle(self, *args, **options):
        previous_key = os.environ.get("PREVIOUS_DIVERSITY_PRIVATE_KEY", None)
        if not previous_key:
            self.stderr.write("Could not find environment variable PREVIOUS_DIVERSITY_PRIVATE_KEY")
            return
        passphrase_old = self.get_old_key_passphrase()

        qs = DiversityDataCheck.get_unprocessed_personal_data_qs(ACTION.REENCRYPT)
        self.stdout.write("Personal data with diversity not null is: {}".format(qs.count()))
        self.create_tasks(qs, passphrase_old)

    def create_tasks(self, qs, passphrase_old):
        total_records = qs.count()
        tasks = []
        for start in range(0, total_records, self.chunk_size):
            end = start + self.chunk_size
            tasks.append(list(qs[start:end].values_list("id", flat=True)))
        self.stdout.write("Processing the number of tasks: {}".format(len(tasks)))
        self.schedule_tasks(tasks, passphrase_old)

    @staticmethod
    def schedule_tasks(tasks, passphrase_old):
        for ids in tasks:
            DiversityDataReencryptTask().delay(passphrase_old, ids)

    @staticmethod
    def get_old_key_passphrase():
        return raw_input("Please enter the passphrase for the PREVIOUS private key:")
