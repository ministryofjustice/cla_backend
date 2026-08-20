# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def create_inquest_category(apps, schema_editor):
    Category = apps.get_model("legalaid", "Category")
    Category.objects.create(
        name="Inquest",
        code="inquest",
        mandatory=False,
        order=99,

    )


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0039_auto_20260701_1113'),
    ]

    operations = [migrations.RunPython(create_inquest_category)]
