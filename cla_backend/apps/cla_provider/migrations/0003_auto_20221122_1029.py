# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("cla_provider", "0002_auto_20150127_1536")]

    operations = [migrations.AlterUniqueTogether(name="staff", unique_together=set([]))]
