# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from django.apps import apps


def get_all_non_restricted_models(models):
    non_restricted_models = []
    # Get all models from all installed apps
    for model in models:
        # Get all columns for each table
        if hasattr(model, "_restrict_analytics"):
            if model._restrict_analytics is False:
                for column in model._meta.get_fields():
                    if not column.is_relation:
                        non_restricted_models.append([model._meta.db_table, column.name])
        # Remove restricted fields from allowed columns
        if hasattr(model, "_restricted_fields"):
            if len(model._restricted_fields) > 0:
                for column in model._restricted_fields:
                    non_restricted_models.remove([model._meta.db_table, column])

    # Returns all allowed columns for user
    return non_restricted_models


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0034_create_anon_user")]

    operations = [
        migrations.RunSQL(
            [
                'GRANT SELECT("{column}") ON {table} TO analytics'.format(column=column, table=table)
                for inner_list in get_all_non_restricted_models(apps.get_models())
                for table, column in [inner_list]
            ]
        )
    ]
