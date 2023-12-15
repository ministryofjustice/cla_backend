# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0034_auto_20231215_0944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personaldetails',
            name='announce_call',
            field=models.BooleanField(default=True),
        ),
    ]
