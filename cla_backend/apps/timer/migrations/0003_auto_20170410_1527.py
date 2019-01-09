# coding=utf-8
from __future__ import unicode_literals

from django.db import models, migrations
import timer.models


class Migration(migrations.Migration):

    dependencies = [("timer", "0002_only_1_running_constraint_20150127_1512")]

    operations = [
        migrations.AlterField(
            model_name="timer",
            name="created",
            field=timer.models.CurrentTimestampDateTimeField(
                default=timer.models.postgres_now, verbose_name="created", editable=False
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="timer",
            name="modified",
            field=models.DateTimeField(auto_now=True, verbose_name="modified"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="timer",
            name="stopped",
            field=timer.models.CurrentTimestampDateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
