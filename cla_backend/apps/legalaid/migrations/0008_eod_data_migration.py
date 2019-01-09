# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


def copy_relation(apps, schema_editor):
    Case = apps.get_model("legalaid", "Case")
    EODDetails = apps.get_model("legalaid", "EODDetails")
    for eod in EODDetails.objects.all():
        try:
            eod.case = eod.old_case
            eod.save()
        except Case.DoesNotExist:
            print("EOD details %s are abandoned, deleting" % eod.reference)
            eod.delete()


class Migration(migrations.Migration):
    dependencies = [("legalaid", "0007_auto_20150818_1509")]
    operations = [migrations.RunPython(copy_relation)]
