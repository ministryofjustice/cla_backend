# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from django.apps import apps

def get_all_non_restricted_models(models):
    non_restricted_models = []

    # Get all models from all installed apps
    for model in models:
        # Construct SQL command to revoke permissions
        if hasattr(model._meta, 'restrict_analytics'):
            if not model._meta.restrict_analytics:
                non_restricted_models.append(model)
    print(non_restricted_models)
    return non_restricted_models

class Migration(migrations.Migration):

    dependencies = [("legalaid", "0034_create_anon_user")]

    operations = [
        migrations.RunSQL(
            ["GRANT ALL PRIVILEGES ON TABLE {model} FROM analytics".format(model=model) for model in get_all_non_restricted_models(apps.get_models())]
            )
    ]
