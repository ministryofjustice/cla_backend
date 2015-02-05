# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


sql = """
ALTER table cla_eventlog_log SET (
    autovacuum_enabled=true,
    autovacuum_analyze_scale_factor=0.0,
    autovacuum_analyze_threshold=5000
);
"""


class Migration(migrations.Migration):

    dependencies = [
        ('cla_eventlog', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(sql)
    ]
