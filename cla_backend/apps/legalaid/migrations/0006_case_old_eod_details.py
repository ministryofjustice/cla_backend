# coding=utf-8
from __future__ import unicode_literals

from django.db import models, migrations


def duplicate_relation(apps, schema_editor):
    Case = apps.get_model("legalaid", "Case")
    for case in Case.objects.all():
        if case.eod_details:
            case.old_eod_details = case.eod_details
            case.save()


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0005_auto_20150814_1136")]

    operations = [
        migrations.AddField(
            model_name="case",
            name="old_eod_details",
            field=models.OneToOneField(
                related_query_name=b"old_case",
                related_name="old_case",
                null=True,
                blank=True,
                to="legalaid.EODDetails",
            ),
            preserve_default=True,
        ),
        migrations.RunPython(duplicate_relation),
    ]
