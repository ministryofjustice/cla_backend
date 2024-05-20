# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('legalaid', '0034_case_callback_type'),]

    operations = [
        migrations.AddField(
            model_name='case',
            name='gtm_anon_id',
            field=models.UUIDField(null=True, blank=True),
        )
    ]
