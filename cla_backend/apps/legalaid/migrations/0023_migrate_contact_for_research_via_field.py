# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Q


def migrate_contact_for_research_via_field_data(apps, schema_editor):
    ContactResearchMethod = apps.get_model("legalaid", "ContactResearchMethod")
    research_methods = {method.method: method.id for method in ContactResearchMethod.objects.all()}
    PersonalDetails = apps.get_model("legalaid", "PersonalDetails")
    models = PersonalDetails.objects.exclude(Q(contact_for_research_via="") | Q(contact_for_research_via=None))
    for model in models:
        if not model.contact_for_research_methods:
            model.contact_for_research_methods = [research_methods.get(model.contact_for_research_via)]
            model.save()


def rollback_migrate_contact_for_research_via_field_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0022_default_contact_for_research_methods")]

    operations = [
        migrations.RunPython(
            migrate_contact_for_research_via_field_data, rollback_migrate_contact_for_research_via_field_data
        )
    ]
