# coding=utf-8
from __future__ import unicode_literals
import logging
from datetime import datetime, time
from itertools import groupby

from cla_eventlog.constants import LOG_LEVELS, LOG_TYPES
from django.db import models, migrations
from django.utils.timezone import now
from pytz import UTC

logger = logging.getLogger(__name__)


def remove_same_day_consecutive_outcome_codes(apps, schema_editor):
    logger.info('LGA-125 data migration: start remove_same_day_consecutive_outcome_codes {}'.format(now()))

    Log = apps.get_model('cla_eventlog', 'Log')

    # Older Django sans TruncDate, etc. not available
    outcome_events = Log.objects.filter(type=LOG_TYPES.OUTCOME, level=LOG_LEVELS.HIGH) \
        .extra(select={'day': 'date( cla_eventlog_log.created )'}) \
        .values('case__reference', 'code', 'day')

    # First pass. Gather case/day/code with >1 occurrences
    cases_with_daily_multiple_events = []
    grouped_results = groupby(outcome_events, key=lambda i: i)
    for (result, g) in grouped_results:
        count = sum(1 for _ in g)
        if count > 1:
            result['count'] = count
            cases_with_daily_multiple_events.append(result)

    # Second pass to reverse chronological scan through all log events for a case on a given day
    # Remove log events where an immediately earlier outcome code is the same
    same_day_consecutive_outcome_log_ids = set()

    for e in cases_with_daily_multiple_events:
        start_of_day = datetime.combine(e['day'], time.min).replace(tzinfo=UTC)
        eod_of_day = datetime.combine(e['day'], time.max).replace(tzinfo=UTC)
        case_outcomes_for_day = Log.objects.filter(case__reference=e['case__reference'],
                                                   type=LOG_TYPES.OUTCOME,
                                                   created__gte=start_of_day,
                                                   created__lte=eod_of_day).order_by('-created')

        n = case_outcomes_for_day.count()
        for index, event in enumerate(case_outcomes_for_day):
            if index < n - 1 and case_outcomes_for_day[index + 1].code == event.code:
                same_day_consecutive_outcome_log_ids.add(event.id)

    logger.info('LGA-125 data migration: To remove, Log objects with id: {}'.format(same_day_consecutive_outcome_log_ids))
    # Log.objects.filter(id__in=same_day_consecutive_outcome_log_ids).delete()
    logger.info('LGA-125 data migration: end remove_same_day_consecutive_outcome_codes {}'.format(now()))


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('cla_eventlog', '0004_auto_20151210_1231'),
        ('legalaid', '0020_fill_missing_outcome_codes'),
    ]

    operations = [
        migrations.RunPython(remove_same_day_consecutive_outcome_codes, noop),
    ]
