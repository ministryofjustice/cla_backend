# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
import datetime
from django.core.management.base import BaseCommand

from legalaid.models import Case


class Command(BaseCommand):
    """
    ./manage.py test_for_call_bunching [minutes] [mnumber_consecutive]
    """

    help = ('Goes through all calls and detects if any provider has had 3 '
            'consecutive calls allocated for the same category in a row')

    def handle(self, *args, **kwargs):
        minutes = 5
        if len(args) > 0:
            minutes = int(args[0])

        number_consecutive = 3
        if len(args) > 1:
            number_consecutive = int(args[1])

        delta = datetime.timedelta(minutes=minutes)

        cases = Case.objects.all().order_by(
            'eligibility_check__category_id',
            'provider_assigned_at'
        ).select_related('eligibility_check')

        total_cases = 0
        total_bunched = 0

        previous = OrderedDict([(i, None) for i in
                                range(1, number_consecutive)])

        for case in cases:
            if case.provider_assigned_at:
                total_cases += 1
            else:
                continue

            earliest_previous = previous[number_consecutive - 1]

            same_provider = None
            same_category = None
            if earliest_previous:
                same_provider = all([c.provider_id == case.provider_id for c
                                     in previous.values()])
                same_category = all([c.eligibility_check.category_id ==
                                     case.eligibility_check.category_id
                                     for c in previous.values()])

            if same_provider and same_category and \
                    case.provider_assigned_at - delta <= \
                    earliest_previous.provider_assigned_at:

                all_pks = ', '.join([unicode(c.pk) for c in previous.values()])

                self.stdout.write('Provider %s has %s cases in %s Minutes: %s'
                                  ', %s on %s' % (case.provider_id,
                                                  number_consecutive, minutes,
                                                  case.pk, all_pks,
                                                  case.provider_assigned_at))
                total_bunched += 1
                for n in range(1, number_consecutive):
                    previous[n] = None
                case = None

            for n in reversed(range(2, number_consecutive)):
                previous[n] = previous[n-1]
            previous[1] = case

        self.stdout.write('\n\nTotal bunched: %s/%s\n\n' % (total_bunched,
                                                            total_cases))



