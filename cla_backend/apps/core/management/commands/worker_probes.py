from django.conf import settings
from django.core.management.base import NoArgsCommand
from cla_backend.celery import app as celery
from legalaid.models import Case


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        self.celery_probe()
        self.database_probe()

    def database_probe(self):
        # Ability to connect to the db; doesn't matter if the result is True or False
        Case.objects.exists()

    def celery_probe(self):
        # Ability to connect to the queue
        # The following will raise an exception if it fails
        with celery.connection_or_acquire() as conn:
            conn.default_channel.queue_declare(queue=settings.CELERY_DEFAULT_QUEUE, passive=True).message_count
