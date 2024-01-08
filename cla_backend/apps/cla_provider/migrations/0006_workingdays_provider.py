# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("cla_provider", "0005_auto_20240108_1047")]

    operations = [
        migrations.AddField(
            model_name="workingdays", name="provider", field=models.ForeignKey(to="cla_provider.Provider", null=True)
        )
    ]
