# coding=utf-8
from django.core.management.base import BaseCommand

from cla_butler.constants import delete_option_three_years
from cla_butler.tasks import DeleteOldData


class Command(BaseCommand):

    help = "Deleting cases that are over three years old and that dont have an excluded outcome_code"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", dest="force", help="Force running of housekeeping task")

    def handle(self, *args, **options):
        self.stdout.write(self.help)
        DeleteOldData().run(delete_option_three_years)
