# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def matter_type1_updates(apps, schema_editor):
    matter_types_to_update = {
        "ESEN": "Special educational needs",
        "EDOT": "Other (ECF Only)",
        "EDDA": "Disability discrimination at school",
        "EEQU": "Contravention of Equality 2010 (non-Disability Discrimination at school)",
    }

    MatterType = apps.get_model("legalaid", "MatterType")
    for code, description in matter_types_to_update.items():
        MatterType.objects.filter(level=1, code=code).update(description=description)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("legalaid", "0025_case_audit_log")]

    operations = [migrations.RunPython(matter_type1_updates, noop)]
