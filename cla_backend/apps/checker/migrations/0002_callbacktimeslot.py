# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [("checker", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="CallbackTimeSlot",
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
                    "time",
                    models.TextField(
                        choices=[
                            (b"0900", b"09:00-09:30"),
                            (b"0930", b"09:30-10:00"),
                            (b"1000", b"10:00-10:30"),
                            (b"1030", b"10:00-10:30"),
                            (b"1100", b"11:00-11:30"),
                            (b"1130", b"11:30-12:00"),
                            (b"1200", b"12:00-12:30"),
                            (b"1230", b"12:30-12:30"),
                            (b"1300", b"13:00-13:30"),
                            (b"1330", b"13:30-14:00"),
                            (b"1400", b"14:00-14:30"),
                            (b"1430", b"14:30-15:00"),
                            (b"1500", b"15:00-15:30"),
                            (b"1530", b"15:30-16:00"),
                            (b"1600", b"16:00-16:30"),
                            (b"1630", b"16:30-17:00"),
                            (b"1700", b"17:00-17:30"),
                            (b"1730", b"17:30-18:00"),
                            (b"1800", b"18:00-18:30"),
                            (b"1830", b"18:30-19:00"),
                            (b"1900", b"19:00-19:30"),
                            (b"1930", b"19:30-20:00"),
                        ]
                    ),
                ),
                ("date", models.DateField()),
                ("capacity", models.IntegerField()),
            ],
            options={"abstract": False},
        )
    ]
