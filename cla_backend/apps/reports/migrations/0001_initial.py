# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Export",
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
                ("path", models.CharField(max_length=255, null=True)),
                (
                    "status",
                    models.CharField(
                        max_length=10,
                        choices=[(b"CREATED", b"created"), (b"FAILED", b"failed"), (b"STARTED", b"started")],
                    ),
                ),
                ("task_id", models.CharField(max_length=100)),
                ("message", models.TextField()),
                ("user", models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        )
    ]
