# -*- coding: utf-8 -*-
import sys
from django.core.management.base import NoArgsCommand

from ...tasks import send_all_performance_data


class Command(NoArgsCommand):
    help = "Starts Celery tasks to send snapshot totals to the Performance platform"

    def handle_noargs(self, **options):
        send_all_performance_data.delay()
