# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0033_personaldetails_announce_call")]

    operations = [
        migrations.RunSQL([
            "CREATE ROLE analytics WITH LOGIN PASSWORD 'password'",
            "GRANT CONNECT ON DATABASE cla_backend TO analytics",
        ])
    ]
