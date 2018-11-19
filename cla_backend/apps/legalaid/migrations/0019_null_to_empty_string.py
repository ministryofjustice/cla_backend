# coding=utf-8
from __future__ import unicode_literals

from django.db import models, migrations


def convert_null_outcome_code_to_empty_string(apps, schema_editor):
    Case = apps.get_model('legalaid', 'Case')
    Case.objects.filter(outcome_code__isnull=True).update(outcome_code='')


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('legalaid', '0018_auto_20180425_1558'),
    ]

    operations = [
        migrations.RunPython(convert_null_outcome_code_to_empty_string, noop),
        migrations.AlterField(
            model_name='case',
            name='outcome_code',
            field=models.CharField(max_length=50, blank=True),
            preserve_default=True,
        ),
    ]
