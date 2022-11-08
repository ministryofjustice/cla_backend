# coding=utf-8
from django.core.management.base import BaseCommand

from cla_butler.constants import delete_option_no_personal_details
from cla_butler.tasks import DeleteOldData


class DeleteCasesWithoutPersonalData(BaseCommand):

    help = "Deleting cases containing no personal data"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", dest="force", help="Force running of housekeeping task")

    def handle(self, *args, **options):
        self.stdout.write(self.help)
        DeleteOldData().run(delete_option_no_personal_details)
