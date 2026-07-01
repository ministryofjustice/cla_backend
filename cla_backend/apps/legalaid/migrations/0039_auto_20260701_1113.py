# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0038_auto_20250409_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personaldetails',
            name='full_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
