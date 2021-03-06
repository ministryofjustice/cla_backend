# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0023_case_callback_window_type")]

    operations = [
        migrations.AlterField(
            model_name="case",
            name="callback_window_type",
            field=models.CharField(
                default=b"HALF_HOUR_WINDOW",
                max_length=50,
                editable=False,
                choices=[
                    (b"HALF_HOUR_EITHER_SIDE", b"Single time, with phone call up to 30 minutes before or after"),
                    (b"HALF_HOUR_WINDOW", b"Half hour time slot"),
                ],
            ),
            preserve_default=True,
        )
    ]
