# coding=utf-8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0014_personaldetails_contact_for_research_via")]

    operations = [
        migrations.AddField(
            model_name="adaptationdetails",
            name="no_adaptations_required",
            field=models.NullBooleanField(),
            preserve_default=True,
        )
    ]
