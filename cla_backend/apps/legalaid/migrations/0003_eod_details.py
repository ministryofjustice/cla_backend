# coding=utf-8
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields
import django.utils.timezone
import uuidfield.fields
import core.cloning


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0002_auto_20150417_1122")]

    operations = [
        migrations.CreateModel(
            name="EODDetails",
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
                ("notes", models.TextField(blank=True)),
                ("reference", uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
            ],
            options={
                "abstract": False,
                "ordering": ("-created",),
                "verbose_name": "EOD details",
                "verbose_name_plural": "EOD details",
            },
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="EODDetailsCategory",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "category",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        null=True,
                        choices=[
                            (b"incorrect", b"Believes operator has given incorrect information"),
                            (b"scope_or_means", b"Negative attitude about scope or means"),
                            (b"delete", b"Wants personal details deleted"),
                            (b"advisor_response", b"No response from specialist advisor, or response delayed"),
                            (b"operator_delay", b"Operator service - delay in advice"),
                            (b"operator_attitude", b"Unhappy with operator's attitude"),
                            (b"advisor_attitude", b"Unhappy with specialist's attitude"),
                            (b"alt_help", b"Alternative help not appropriate or not available"),
                            (b"public_tool", b"Unhappy with online service"),
                            (b"adaptations", b"Problems with adaptations or adjustments"),
                            (b"scope_assessment", b"Scope reassessment requested"),
                            (b"means_assessment", b"Financial reassessment requested"),
                            (
                                b"pass_to_public",
                                b"Threatens to pass the matter on to the media, or other public or regulatory body",
                            ),
                            (b"data_protection", b"Breach of Data Protection Act/policy and confidentiality"),
                            (b"discrimination", b"Discrimination from an operator or specialist"),
                            (b"plo_referral", b"Client unhappy with PLO referral"),
                            (b"other", b"Other"),
                        ],
                    ),
                ),
                ("is_major", models.BooleanField(default=False)),
                ("eod_details", models.ForeignKey(related_name="categories", to="legalaid.EODDetails")),
            ],
            options={"abstract": False, "verbose_name": "EOD category", "verbose_name_plural": "EOD categories"},
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name="case",
            name="eod_details",
            field=models.ForeignKey(blank=True, to="legalaid.EODDetails", null=True),
            preserve_default=True,
        ),
    ]
