# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0007_auto_20150818_1509'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='old_eod_details',
        ),
        migrations.AlterField(
            model_name='eoddetails',
            name='case',
            field=models.OneToOneField(related_query_name=b'eod_details', related_name='eod_details', to='legalaid.Case'),
            preserve_default=True,
        ),
    ]
