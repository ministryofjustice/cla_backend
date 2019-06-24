# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields
import uuidfield.fields
import core.cloning


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0020_fill_missing_outcome_codes")]

    operations = [
        migrations.CreateModel(
            name="ContactResearchMethod",
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
                ("method", models.CharField(default=b"PHONE", max_length=10, null=True, blank=True)),
                ("reference", uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
            ],
            options={"abstract": False},
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name="personaldetails",
            name="contact_for_research_methods",
            field=models.ManyToManyField(to="legalaid.ContactResearchMethod", null=True),
            preserve_default=True,
        ),
    ]
