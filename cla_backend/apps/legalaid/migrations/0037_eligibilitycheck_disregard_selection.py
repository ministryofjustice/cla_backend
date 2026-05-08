# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0036_auto_20241002_1407")]

    operations = [
        migrations.AddField(
            model_name="eligibilitycheck",
            name="disregard_selection",
            field=models.CharField(
                default=None,
                max_length=10,
                null=True,
                blank=True,
                choices=[(b"yes", b"Yes"), (b"no", b"No"), (b"not_sure", b"Not sure")],
            ),
        )
    ]
