# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0003_eod_details")]

    operations = [
        migrations.CreateModel(
            name="ReasonForContacting",
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
                ("reference", uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ("other_reasons", models.TextField(blank=True)),
                ("referrer", models.CharField(max_length=255, blank=True)),
                ("user_agent", models.CharField(max_length=255, blank=True)),
                ("case", models.ForeignKey(blank=True, to="legalaid.Case", null=True)),
            ],
            options={"ordering": ("-created",), "verbose_name_plural": "reasons for contacting"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ReasonForContactingCategory",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "category",
                    models.CharField(
                        max_length=20,
                        choices=[
                            (b"CANT_ANSWER", "I don\u2019t know how to answer a question"),
                            (b"MISSING_PAPERWORK", "I don\u2019t have the paperwork I need"),
                            (b"PREFER_SPEAKING", "I\u2019d prefer to speak to someone"),
                            (b"DIFFICULTY_ONLINE", "I have trouble using online services"),
                            (b"HOW_SERVICE_HELPS", "I don\u2019t understand how this service can help me"),
                            (b"AREA_NOT_COVERED", "My problem area isn\u2019t covered"),
                            (b"PNS", "I\u2019d prefer not to say"),
                            (b"OTHER", "Another reason"),
                        ],
                    ),
                ),
                ("reason_for_contacting", models.ForeignKey(related_name="reasons", to="checker.ReasonForContacting")),
            ],
            options={"verbose_name": "category", "verbose_name_plural": "categories"},
            bases=(models.Model,),
        ),
    ]
