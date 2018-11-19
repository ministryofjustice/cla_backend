# coding=utf-8
from __future__ import unicode_literals
import logging

from django.db import models, migrations

logger = logging.getLogger(__name__)


def re_denormalize_outcome_codes_to_cases(apps, schema_editor):
    try:
        from cla_eventlog.constants import LOG_LEVELS, LOG_TYPES
        from cla_eventlog.models import Log
    except ImportError:
        pass
    else:
        outcomes_that_should_be_denormed = Log.objects.filter(level=LOG_LEVELS.HIGH, type=LOG_TYPES.OUTCOME)
        outcomes_missing_denormed_code = outcomes_that_should_be_denormed.filter(case__outcome_code='')

        logger.info('\nLGA-275 data migration: {} outcomes_missing_denormed_code'.format(outcomes_missing_denormed_code.count()))
        for outcome in outcomes_missing_denormed_code:
            outcome.case.outcome_code = outcome.code
            outcome.case.save()
            logger.info('LGA-275 data migration: Filled missing outcome code for case {}'.format(outcome.case.reference))


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('legalaid', '0019_null_to_empty_string'),
    ]

    operations = [
        migrations.RunPython(re_denormalize_outcome_codes_to_cases, noop),
    ]
