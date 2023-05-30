import os
from django.core.management.base import BaseCommand
from cla_butler.tasks import DiversityDataReencryptTask
from cla_butler.models import DiversityDataCheck, ACTION
from legalaid.utils import diversity


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
        if total_records <= 0:
            self.stderr.write("Found no records to re-encrypt")
            return

        tasks = []
        for start in range(0, total_records, self.chunk_size):
            end = start + self.chunk_size
            tasks.append(list(qs[start:end].values_list("id", flat=True)))
        self.stdout.write("Processing the number of tasks: {}".format(len(tasks)))
        self.schedule_tasks(tasks, passphrase_old)

    def schedule_tasks(self, tasks, passphrase_old):
        # Try to decrypt some sample items using the old key and given passphrase before
        # starting the full re-encryption process
        self.stdout.write("Attempting to decrypt sample data before starting full re-encryption proces")
        private_key_override = os.environ["PREVIOUS_DIVERSITY_PRIVATE_KEY"].replace("\\n", "\n")
        sample_items = tasks[0][:5]
        for item in sample_items:
            try:
                diversity.load_diversity_data(item, passphrase_old, private_key_override=private_key_override)
            except Exception as error:
                self.stderr.write("Could not decrypt sample data({}): {}".format(item, str(error)))
                return
        self.stdout.write("All sample data have been successfully been decrypted. Scheduling tasks for re-encryption")
        # Schedule celery tasks to re-encrypt the existing diversity data
        for ids in tasks:
            DiversityDataReencryptTask().delay(passphrase_old, ids)
        self.stdout.write("All tasks have been rescheduled for re-encryption")

    @staticmethod
    def get_old_key_passphrase():
        return raw_input("Please enter the passphrase for the PREVIOUS private key:")
