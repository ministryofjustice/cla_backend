# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [("call_centre", "0002_caseworker")]

    operations = [
        migrations.CreateModel(
            name="Organisation",
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
                ("name", models.CharField(unique=True, max_length=255)),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="operator",
            name="organisation",
            field=models.ForeignKey(blank=True, to="call_centre.Organisation", null=True),
            preserve_default=True,
        ),
    ]
