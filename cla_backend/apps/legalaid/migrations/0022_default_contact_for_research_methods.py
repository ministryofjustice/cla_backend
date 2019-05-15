# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import uuid
from cla_common.constants import RESEARCH_CONTACT_VIA


def create_default_contact_for_research_methods(apps, schema_editor):
    ContactResearchMethods = apps.get_model("legalaid", "ContactResearchMethod")
    for value, name in RESEARCH_CONTACT_VIA:
        ContactResearchMethods.objects.create(method=value, reference=uuid.uuid4()).save()


def rollback_default_contact_for_research_methods(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0021_auto_20190515_1042")]

    operations = [
        migrations.RunPython(
            create_default_contact_for_research_methods, rollback_default_contact_for_research_methods
        )
    ]
