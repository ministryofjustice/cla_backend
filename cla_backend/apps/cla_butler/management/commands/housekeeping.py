# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from cla_butler.tasks import DeleteOldData


class Command(BaseCommand):

    help = 'Deletes public diagnosis that are more than a day old'

    def handle(self, *args, **options):
        DeleteOldData().run()
