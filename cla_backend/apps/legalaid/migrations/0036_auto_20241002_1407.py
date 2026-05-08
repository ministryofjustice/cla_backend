# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0035_case_gtm_anon_id")]

    operations = [
        migrations.AlterModelOptions(
            name="case",
            options={
                "ordering": ("-created",),
                "permissions": (
                    ("run_reports", "Can run reports"),
                    ("run_obiee_reports", "Can run OBIEE reports"),
                    ("run_complaints_report", "Can run complaints report"),
                    ("run_internal_reports", "Can run internal reports"),
                ),
            },
        )
    ]
