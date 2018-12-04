# coding=utf-8
from __future__ import unicode_literals
import logging

from django.db import models, migrations
from django.db.models import Count, Max, Min

logger = logging.getLogger(__name__)


def remove_same_day_consecutive_outcome_codes(apps, schema_editor):
    from cla_eventlog.constants import LOG_LEVELS, LOG_TYPES
    Log = apps.get_model('cla_eventlog', 'Log')

    # from cla_eventlog.models import Log
    outcome_events = Log.objects.filter(type=LOG_TYPES.OUTCOME, level=LOG_LEVELS.HIGH)
    outcome_events = outcome_events.extra(select={'day': 'date( cla_eventlog_log.created )'})
    outcome_events = outcome_events.only('case__reference', 'code', 'day')
    outcome_event_counts = outcome_events.values('case__reference', 'code', 'day').annotate(total=Count('code'))
    outcome_event_counts = outcome_events.values('case__reference', 'code', 'day').annotate(day_total=Count('day'))
    multiple_codes_today = outcome_event_counts.filter(total__gt=1).order_by('-total')


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('cla_eventlog', '0004_auto_20151210_1231'),
    ]

    operations = [
        migrations.RunPython(remove_same_day_consecutive_outcome_codes, noop),
    ]
