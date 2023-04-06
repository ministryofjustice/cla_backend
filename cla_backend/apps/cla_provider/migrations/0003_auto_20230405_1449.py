# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("cla_provider", "0002_auto_20150127_1536")]

    operations = [
        migrations.AlterField(
            model_name="provider",
            name="name",
            field=models.CharField(unique=True, max_length=255),
            preserve_default=True,
        )
    ]
