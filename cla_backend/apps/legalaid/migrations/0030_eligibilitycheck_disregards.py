# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0029_auto_20211213_1144")]

    operations = [
        migrations.AddField(
            model_name="eligibilitycheck",
            name="disregards",
            field=jsonfield.fields.JSONField(null=True, blank=True),
            preserve_default=True,
        )
    ]
