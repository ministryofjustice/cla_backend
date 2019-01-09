# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("diagnosis", "0002_auto_20150127_1536")]

    operations = [
        migrations.AlterField(
            model_name="diagnosistraversal",
            name="state",
            field=models.CharField(default=b"UNKNOWN", max_length=50, null=True, db_index=True, blank=True),
            preserve_default=True,
        )
    ]
