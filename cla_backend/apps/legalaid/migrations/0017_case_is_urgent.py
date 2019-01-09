# coding=utf-8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0016_auto_20170223_1150")]

    operations = [
        migrations.AddField(
            model_name="case", name="is_urgent", field=models.BooleanField(default=False), preserve_default=True
        )
    ]
