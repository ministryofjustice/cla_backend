# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("cla_provider", "0003_auto_20230405_1449")]

    operations = [migrations.AlterUniqueTogether(name="staff", unique_together=set([]))]
