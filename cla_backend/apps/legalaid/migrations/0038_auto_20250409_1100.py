# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("checker", "0003_scopetraversal"), ("legalaid", "0037_eligibilitycheck_disregard_selection")]

    operations = [
        migrations.AddField(model_name="case", name="client_notes", field=models.TextField(blank=True)),
        migrations.AddField(
            model_name="case",
            name="scope_traversal",
            field=models.OneToOneField(null=True, blank=True, to="checker.ScopeTraversal"),
        ),
    ]
