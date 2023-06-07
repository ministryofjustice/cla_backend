# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("cla_provider", "0003_auto_20221122_1029")]

    operations = [
        migrations.AlterField(
            model_name="provider",
            name="name",
            field=models.CharField(unique=True, max_length=255),
            preserve_default=True,
        )
    ]
