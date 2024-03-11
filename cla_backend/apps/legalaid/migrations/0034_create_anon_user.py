# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0033_personaldetails_announce_call")]

    db_password = os.environ.get("ANALYTICS_DB_PASSWORD")

    operations = [
        migrations.RunSQL(
            [
                "CREATE ROLE analytics WITH LOGIN PASSWORD '{db_password}'",
                "GRANT CONNECT ON DATABASE cla_backend TO analytics",
            ]
        )
    ]
