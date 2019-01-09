# coding=utf-8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0003_eod_details")]

    operations = [
        migrations.AlterField(
            model_name="property",
            name="eligibility_check",
            field=models.ForeignKey(related_query_name=b"property_set", to="legalaid.EligibilityCheck"),
            preserve_default=True,
        )
    ]
