# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from cla_common.constants import CONTACT_SAFETY


def migrate_no_message_to_safe_to_contact(apps, schema_editor):
    PersonalDetails = apps.get_model("legalaid", "PersonalDetails")
    PersonalDetails.objects.filter(safe_to_contact="NO_MESSAGE").update(safe_to_contact=CONTACT_SAFETY.SAFE)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0025_case_audit_log")]

    operations = [
        migrations.RunPython(migrate_no_message_to_safe_to_contact, noop),
        migrations.AlterField(
            model_name="personaldetails",
            name="safe_to_contact",
            field=models.CharField(
                default=b"SAFE",
                max_length=30,
                null=True,
                blank=True,
                choices=[(b"SAFE", b"Safe to contact"), (b"DONT_CALL", b"Not safe to call")],
            ),
            preserve_default=True,
        ),
    ]
