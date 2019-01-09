# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


sql = """
CREATE UNIQUE INDEX timer_single_running
    ON timer_timer (created_by_id)
    WHERE (cancelled = FALSE and stopped IS NULL);
"""


class Migration(migrations.Migration):

    dependencies = [("timer", "0001_initial")]

    operations = [migrations.RunSQL(sql)]
