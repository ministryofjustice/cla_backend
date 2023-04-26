# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("cla_butler", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="diversitydatacheck",
            name="action",
            field=models.CharField(max_length=20, choices=[(b"check", b"Check"), (b"reencrypt", b"Re-encrypt")]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="diversitydatacheck",
            name="personal_details",
            field=models.ForeignKey(to="legalaid.PersonalDetails"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="diversitydatacheck",
            name="status",
            field=models.CharField(max_length=10, choices=[(b"ok", b"OK"), (b"fail", b"Fail")]),
            preserve_default=True,
        ),
    ]
