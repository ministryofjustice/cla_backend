# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import django.utils.timezone
import model_utils.fields
import uuidfield.fields
import core.cloning


class Migration(migrations.Migration):

    dependencies = [("checker", "0002_callbacktimeslot")]

    operations = [
        migrations.CreateModel(
            name="ScopeTraversal",
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
                ("scope_answers", jsonfield.fields.JSONField(default=dict)),
                ("category", jsonfield.fields.JSONField(default=dict)),
                ("subcategory", jsonfield.fields.JSONField(default=dict)),
                (
                    "financial_assessment_status",
                    models.CharField(
                        max_length=32,
                        null=True,
                        choices=[
                            (b"PASSED", b"Passed"),
                            (b"FAILED", b"Failed"),
                            (b"FAST_TRACK", b"Client told to call the helpline for the assessment."),
                            (b"SKIPPED", b"No details. Client called the helpline directly."),
                        ],
                    ),
                ),
                (
                    "fast_track_reason",
                    models.CharField(
                        max_length=32,
                        null=True,
                        choices=[
                            (b"HARM", b"User has indicated they are at risk of harm"),
                            (b"MORE_INFO_REQUIRED", b"Further scoping information is required"),
                            (b"OTHER", b"Other"),
                        ],
                    ),
                ),
                ("reference", uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
            ],
            options={"abstract": False},
            bases=(core.cloning.CloneModelMixin, models.Model),
        )
    ]
