# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0028_eligibilitycheck_has_passported_proceedings_letter")]

    operations = [
        migrations.AlterField(
            model_name="case",
            name="ecf_statement",
            field=models.CharField(
                blank=True,
                max_length=35,
                null=True,
                choices=[
                    (
                        b"XFER_TO_RECORDED_MESSAGE",
                        b'\n        "On closing this call you will hear a recorded message which will contain information to highlight limited\n         circumstances in which legal aid may still be available to you. Thank you [client name] for calling\n         Civil Legal Advice. Goodbye"\n        ',
                    ),
                    (
                        b"READ_OUT_MESSAGE",
                        b'\n        "Legal aid may be available in exceptional circumstances to people whose cases are out of scope where a refusal\n         to fund would breach Human Rights or enforceable European law. You could seek advice from a legal advisor\n         about whether an application might succeed in your case and how to make one. Thank you for calling\n         Civil Legal Advice. Goodbye"\n        ',
                    ),
                    (b"PROBLEM_NOT_SUITABLE", b""),
                    (b"CLIENT_TERMINATED", b""),
                ],
            ),
            preserve_default=True,
        )
    ]
