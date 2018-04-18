# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0017_case_is_urgent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='requires_action_at',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personaldetails',
            name='date_of_birth',
            field=models.DateField(db_index=True, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personaldetails',
            name='full_name',
            field=models.CharField(db_index=True, max_length=400, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personaldetails',
            name='postcode',
            field=models.CharField(db_index=True, max_length=12, null=True, blank=True),
            preserve_default=True,
        ),
    ]
