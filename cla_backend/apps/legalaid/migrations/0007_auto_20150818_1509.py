# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0006_case_old_eod_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='eod_details',
        ),
        migrations.AddField(
            model_name='eoddetails',
            name='case',
            field=models.OneToOneField(related_query_name=b'eod_details', related_name='eod_details', null=True, to='legalaid.Case'),
            preserve_default=False,
        ),
    ]
