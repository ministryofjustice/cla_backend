# coding=utf-8
import datetime
from django.core.management.base import BaseCommand
from cla_butler.tasks import DiversityDataCheckTask
from cla_butler.models import DiversityDataCheck, ACTION
from legalaid.utils import diversity


class Command(BaseCommand):

    help = "Checks all the diversity data is encrypted with the same set of keys"

    def handle(self, *args, **options):
        self.stdout.write("This will check all the diversity data is encrypted with the same set of keys")
        self.stdout.write(
            "It will go through all rows in the legalaid_personaldata table and attempt to decrypt the diversity data using current private key"
        )
        qs = DiversityDataCheck.get_unprocessed_personal_data_qs(ACTION.CHECK)
        self.stdout.write("Personal data with diversity not null is: {}".format(qs.count()))
        passphrase = self.get_passphrase()
        try:
            diversity.load_diversity_data(qs[0].pk, passphrase)
        except Exception as e:
            self.stderr.write("Could not decrypt data using passphrase: {error}".format(error=str(e)))
        else:
            self.schedule_tasks(qs, 1000, passphrase)

    def schedule_tasks(self, qs, chunk_size, passphrase):
        total_records = qs.count()
        counter = 1
        eta = datetime.datetime.now() + datetime.timedelta(seconds=30)
        for start in range(0, total_records, chunk_size):
            end = start + chunk_size
            ids = list(qs[start:end].values_list("id", flat=True))
            description = "{index} - {start}:{end} {count} items".format(
                index=counter, start=start, end=end, count=len(ids)
            )
            self.stdout.write(description)
            # Need to add a delay otherwise the query will be inaccurate as celery tasks starts processing records
            DiversityDataCheckTask().apply_async((passphrase, ids, description), eta=eta)
            counter += 1

    @staticmethod
    def get_passphrase():
        return raw_input("Please enter the passphrase for the CURRENT private key:")
