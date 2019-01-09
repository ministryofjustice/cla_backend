# coding=utf-8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0013_auto_20160414_1429")]

    operations = [
        migrations.AddField(
            model_name="personaldetails",
            name="contact_for_research_via",
            field=models.CharField(
                default=b"PHONE",
                max_length=10,
                null=True,
                blank=True,
                choices=[(b"EMAIL", b"Email"), (b"PHONE", b"Phone"), (b"SMS", b"Sms")],
            ),
            preserve_default=True,
        )
    ]
