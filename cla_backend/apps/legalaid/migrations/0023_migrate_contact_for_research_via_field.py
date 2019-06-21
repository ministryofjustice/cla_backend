# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def migrate_contact_for_research_via_field_data(apps, schema_editor):
    ContactResearchMethod = apps.get_model("legalaid", "ContactResearchMethod")
    PersonalDetails = apps.get_model("legalaid", "PersonalDetails")

    for method in ContactResearchMethod.objects.all():
        details_qs = PersonalDetails.objects.filter(
            contact_for_research_via=method.method, contact_for_research_methods__isnull=True
        )
        for details in details_qs:
            details.contact_for_research_methods.add(method)


def rollback_migrate_contact_for_research_via_field_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0022_default_contact_for_research_methods")]

    operations = [
        migrations.RunPython(
            migrate_contact_for_research_via_field_data, rollback_migrate_contact_for_research_via_field_data
        )
    ]
