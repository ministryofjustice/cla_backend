# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0032_auto_20230719_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='personaldetails',
            name='announce_call',
            field=models.BooleanField(default=False),
        ),
    ]
