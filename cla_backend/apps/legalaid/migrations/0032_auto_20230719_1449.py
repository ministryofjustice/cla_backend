# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0031_personal_details_contact_for_research_method")]

    operations = [
        migrations.AddField(
            model_name="eligibilitycheck", name="is_you_under_18", field=models.NullBooleanField(default=None)
        ),
        migrations.AddField(
            model_name="eligibilitycheck", name="under_18_has_valuables", field=models.NullBooleanField(default=None)
        ),
        migrations.AddField(
            model_name="eligibilitycheck", name="under_18_passported", field=models.NullBooleanField(default=None)
        ),
        migrations.AddField(
            model_name="eligibilitycheck",
            name="under_18_receive_regular_payment",
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name="personaldetails", name="email", field=models.EmailField(max_length=254, blank=True)
        ),
    ]
