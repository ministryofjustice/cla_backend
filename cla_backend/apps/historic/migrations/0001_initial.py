# coding=utf-8
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CaseArchived",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, verbose_name="created", editable=False
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, verbose_name="modified", editable=False
                    ),
                ),
                ("full_name", models.TextField(null=True, blank=True)),
                ("date_of_birth", models.DateField(null=True, blank=True)),
                ("postcode", models.CharField(max_length=12, null=True, blank=True)),
                ("laa_reference", models.BigIntegerField(unique=True, null=True, editable=False, blank=True)),
                ("specialist_referred_to", models.TextField(null=True, blank=True)),
                ("date_specialist_referred", models.DateTimeField(null=True, blank=True)),
                ("date_specialist_closed", models.DateTimeField(null=True, blank=True)),
                ("knowledgebase_items_used", models.TextField(null=True, blank=True)),
                ("area_of_law", models.TextField(null=True, blank=True)),
                ("in_scope", models.NullBooleanField()),
                ("financially_eligible", models.NullBooleanField()),
                ("outcome_code", models.TextField(null=True, blank=True)),
                ("outcome_code_date", models.DateTimeField(null=True, blank=True)),
                ("search_field", models.TextField(null=True, blank=True)),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        )
    ]
