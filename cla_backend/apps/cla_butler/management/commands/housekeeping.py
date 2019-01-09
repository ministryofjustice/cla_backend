# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from cla_butler.stack import is_first_instance, InstanceNotInAsgException, StackException
from cla_butler.tasks import DeleteOldData


class Command(BaseCommand):

    help = "Deletes public diagnosis that are more than a day old"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", dest="force", help="Force running of housekeeping task")

    def handle(self, *args, **options):
        if self.should_run_housekeeping(**options):
            DeleteOldData().run()
        else:
            self.stdout.write("Not doing housekeeping because running on secondary instance")

    def should_run_housekeeping(self, **options):
        if options.get("force", False):
            return True

        try:
            return is_first_instance()
        except InstanceNotInAsgException:
            self.stderr.write("EC2 instance not in an ASG")
            return True
        except StackException:
            self.stderr.write("Not running on EC2 instance")
            return True
