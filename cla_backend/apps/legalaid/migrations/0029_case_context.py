# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0028_eligibilitycheck_has_passported_proceedings_letter")]

    operations = [
        migrations.AddField(
            model_name="case",
            name="context",
            field=jsonfield.fields.JSONField(
                help_text=b"Field to store extra case data for reporting", null=True, blank=True
            ),
            preserve_default=True,
        )
    ]
