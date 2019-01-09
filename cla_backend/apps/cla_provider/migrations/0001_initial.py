# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations
import django.utils.timezone
import core.validators
import jsonfield.fields
import model_utils.fields
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="CSVUpload",
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
                ("comment", models.TextField(null=True, blank=True)),
                ("body", jsonfield.fields.JSONField()),
                ("month", models.DateField(validators=[core.validators.validate_first_of_month])),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Feedback",
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
                ("comment", models.TextField()),
                ("justified", models.BooleanField(default=False)),
                ("resolved", models.BooleanField(default=False)),
                (
                    "issue",
                    models.CharField(
                        max_length=100,
                        choices=[
                            (b"ADCO", b"Advisor conduct"),
                            (b"ACPR", b"Access problems"),
                            (b"ARRA", b"Already receiving/received advice"),
                            (b"COLI", b"Category of law is incorrect"),
                            (b"DLAY", b"Delay in advising (lack of follow up information)"),
                            (b"DLAO", b"Delay in advising (other)"),
                            (b"INEL", b"Incorrect eligibility calculation"),
                            (b"INDI", b"Incorrect diagnosis (out of scope)"),
                            (b"INIP", b"Incorrect information provided (diagnosis)"),
                            (b"INTC", b"Incorrect transferring of calls (provider)"),
                            (b"INFB", b"Incorrect transferring of calls (front/back)"),
                            (b"IMCD", b"Incorrect/missing contact details or DOB"),
                            (b"ODDE", b"Other data entry errors"),
                            (b"SESE", b"System Error"),
                            (b"OTHR", b"Other"),
                        ],
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="OutOfHoursRota",
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
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Provider",
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
                ("name", models.CharField(max_length=255)),
                ("opening_hours", models.CharField(max_length=100, blank=True)),
                ("active", models.BooleanField(default=False)),
                ("short_code", models.CharField(max_length=100, blank=True)),
                ("telephone_frontdoor", models.CharField(max_length=100, blank=True)),
                ("telephone_backdoor", models.CharField(max_length=100, blank=True)),
                ("email_address", models.EmailField(max_length=75, blank=True)),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ProviderAllocation",
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
                ("weighted_distribution", models.FloatField()),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ProviderPreAllocation",
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
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Staff",
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
                ("is_manager", models.BooleanField(default=False)),
                (
                    "chs_organisation",
                    models.CharField(
                        help_text=b"Fake field to mirror old CHS extract, user can set this to whatever they like",
                        max_length=500,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "chs_user",
                    models.CharField(
                        help_text=b"Fake field to mirror old CHS extract, user can set this to whatever they like",
                        max_length=500,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "chs_password",
                    models.CharField(
                        help_text=b"Fake field to mirror old CHS extract, user can set this to whatever they like",
                        max_length=500,
                        null=True,
                        blank=True,
                    ),
                ),
                ("provider", models.ForeignKey(to="cla_provider.Provider")),
                ("user", models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name_plural": "staff"},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(name="staff", unique_together=set([("chs_organisation", "chs_user")])),
    ]
