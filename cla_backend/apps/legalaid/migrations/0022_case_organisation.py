# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("call_centre", "0003_auto_20190729_1416"), ("legalaid", "0021_auto_20190515_1042")]

    operations = [
        migrations.AddField(
            model_name="case",
            name="organisation",
            field=models.ForeignKey(blank=True, to="call_centre.Organisation", null=True),
            preserve_default=True,
        )
    ]
