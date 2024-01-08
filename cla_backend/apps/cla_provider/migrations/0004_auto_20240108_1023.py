# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("cla_provider", "0003_auto_20230405_1449")]

    operations = [
        migrations.CreateModel(
            name="WorkingDays",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("monday", models.BooleanField(default=True)),
                ("tuesday", models.BooleanField(default=True)),
                ("wednesday", models.BooleanField(default=True)),
                ("thursday", models.BooleanField(default=True)),
                ("friday", models.BooleanField(default=True)),
            ],
            options={"verbose_name": "Working Days", "verbose_name_plural": "Working Days - Education only"},
        ),
        migrations.AlterField(
            model_name="provider", name="email_address", field=models.EmailField(max_length=254, blank=True)
        ),
        migrations.AddField(
            model_name="providerallocation",
            name="workday_days",
            field=models.ForeignKey(to="cla_provider.WorkingDays", null=True),
        ),
    ]
