# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0033_adaptationdetails_announce_call_from_cla'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adaptationdetails',
            name='announce_call',
        ),
        migrations.AddField(
            model_name='personaldetails',
            name='announce_call',
            field=models.NullBooleanField(),
        ),
    ]
