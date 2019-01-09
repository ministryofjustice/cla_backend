# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("contenttypes", "0001_initial"), ("cla_eventlog", "0002_analyse_20150127_1540")]

    operations = [
        migrations.CreateModel(
            name="ComplaintLog", fields=[], options={"abstract": False, "proxy": True}, bases=("cla_eventlog.log",)
        ),
        migrations.AddField(
            model_name="log",
            name="content_type",
            field=models.ForeignKey(blank=True, to="contenttypes.ContentType", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="log",
            name="object_id",
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="log",
            name="type",
            field=models.CharField(
                max_length=20, choices=[(b"outcome", b"outcome"), (b"system", b"system"), (b"event", b"event")]
            ),
            preserve_default=True,
        ),
    ]
