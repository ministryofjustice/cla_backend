# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0030_eligibilitycheck_disregards")]

    operations = [
        migrations.AlterField(
            model_name="personaldetails",
            name="contact_for_research_methods",
            field=models.ManyToManyField(to="legalaid.ContactResearchMethod", null=True, blank=True),
            preserve_default=True,
        )
    ]
