# coding=utf-8
from django.core.management.base import BaseCommand

from cla_butler.tasks import DeleteOldData


class Command(BaseCommand):

    help = "Deletes public diagnosis that are more than a day old"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", dest="force", help="Force running of housekeeping task")

    def handle(self, *args, **options):
        self.stdout.write("Deleting public diagnosis that are more than a day old")
        DeleteOldData().run()
