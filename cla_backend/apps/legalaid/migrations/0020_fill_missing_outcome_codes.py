# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def re_denormalize_outcome_codes_to_cases(apps, schema_editor):
    try:
        from cla_eventlog.constants import LOG_LEVELS, LOG_TYPES
    except ImportError:
        pass
    else:
        Case = apps.get_model('legalaid', 'Case')
        Log = apps.get_model('cla_eventlog', 'Log')

        outcomes_that_should_be_denormed = Log.objects.filter(level=LOG_LEVELS.HIGH, type=LOG_TYPES.OUTCOME)
        outcomes_missing_denormed_code = outcomes_that_should_be_denormed.filter(case__outcome_code='')
        outcomes_missing_denormed_code_pks = outcomes_missing_denormed_code.values_list('id', flat=True)
        cases_to_re_denorm = Case.objects.filter(outcome_code='', outcome_code_id__isnull=False,
                                                 log_set__id__in=outcomes_missing_denormed_code_pks)

        for case in cases_to_re_denorm.all():
            # Lookup latest approach
            # outcome = case.log_set.filter(level=LOG_LEVELS.HIGH, type=LOG_TYPES.OUTCOME).latest('created')
            # TODO or earliest? Ask Jenny
            # case.outcome_code = outcome.code
            # case.save()

            # Fetch via id approach
            outcome = Log.objects.filter(id=case.outcome_code_id).first()
            if outcome:
                case.outcome_code = outcome.code
                case.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('legalaid', '0018_auto_20180425_1558'),
    ]

    operations = [
        migrations.RunPython(re_denormalize_outcome_codes_to_cases, noop),
    ]
