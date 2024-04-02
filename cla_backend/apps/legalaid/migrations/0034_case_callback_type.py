# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0033_personaldetails_announce_call")]

    operations = [
        migrations.AddField(
            model_name="case",
            name="callback_type",
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                choices=[
                    (b"chs_operator", b"CHS Operator"),
                    (b"web_form_self", b"Web Form - Self"),
                    (b"web_form_third_party", b"Web Form - Third Party"),
                ],
            ),
        )
    ]
