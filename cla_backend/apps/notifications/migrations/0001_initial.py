# coding=utf-8
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Notification",
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
                (
                    "type",
                    models.CharField(
                        default=b"notification",
                        max_length=20,
                        choices=[("alert", "Alert"), ("notification", "Notification")],
                    ),
                ),
                ("notification", models.CharField(max_length=100)),
                ("description", models.CharField(max_length=600, null=True, blank=True)),
                ("notes", models.TextField(null=True, blank=True)),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("created_by", models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        )
    ]
