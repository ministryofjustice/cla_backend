# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0011_case_assigned_out_of_hours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='assigned_out_of_hours',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
    ]
