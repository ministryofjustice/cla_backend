# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("cla_provider", "0004_auto_20240108_1023")]

    operations = [
        migrations.RenameField(model_name="providerallocation", old_name="workday_days", new_name="working_days")
    ]
