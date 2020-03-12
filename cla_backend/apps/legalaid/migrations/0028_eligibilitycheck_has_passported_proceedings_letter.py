# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0027_update_education_matter_type1_descriptions")]

    operations = [
        migrations.AddField(
            model_name="eligibilitycheck",
            name="has_passported_proceedings_letter",
            field=models.NullBooleanField(default=None),
            preserve_default=True,
        )
    ]
