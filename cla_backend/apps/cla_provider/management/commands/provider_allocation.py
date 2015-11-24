# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
import datetime
import pytz

from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from legalaid.models import Case, Category

from ...helpers import ProviderDistributionHelper
from ...models import Provider, ProviderAllocation


class Command(BaseCommand):
    """
    ./manage.py provider_allocation [from_date 2015-11-02]
    """

    help = ('Gets provider allocations per category for period with no '
            'weighting changes')

    def handle(self, *args, **kwargs):
        if len(args):
            from_date = datetime.datetime.strptime(args[0], '%Y-%m-%d').replace(tzinfo=pytz.utc)
        else:
            from_date = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        pd = ProviderDistributionHelper(from_date)
        for category in Category.objects.all():
            last_update = ProviderAllocation.objects.filter(category=category).order_by('-modified').first()
            self.stdout.write('\n')
            self.stdout.write(category.name)
            self.stdout.write('=' * len(category.name))
            if last_update:
                self.stdout.write('ALLOCATION WEIGHT UPDATED ON: %s' % last_update.modified)
            for provider_id, allocation in pd.get_distribution(category).items():
                provider = Provider.objects.get(pk=provider_id)
                provider_allocation = ProviderAllocation.objects.filter(
                    provider=provider,
                    category=category).order_by('-modified').first()
                weighting = provider_allocation.weighted_distribution if \
                    provider_allocation else 'None'
                self.stdout.write('%s: %s(%s)' %(provider.name, allocation,
                                                 weighting))