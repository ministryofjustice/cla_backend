# coding=utf-8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("cla_eventlog", "0003_auto_20150813_1431")]

    operations = [
        migrations.AlterField(
            model_name="log", name="code", field=models.CharField(max_length=50, db_index=True), preserve_default=True
        ),
        migrations.AlterField(
            model_name="log",
            name="level",
            field=models.PositiveSmallIntegerField(
                db_index=True, choices=[(29, b"HIGH"), (21, b"MODERATE"), (11, b"MINOR")]
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="log",
            name="type",
            field=models.CharField(
                db_index=True,
                max_length=20,
                choices=[(b"outcome", b"outcome"), (b"system", b"system"), (b"event", b"event")],
            ),
            preserve_default=True,
        ),
    ]
