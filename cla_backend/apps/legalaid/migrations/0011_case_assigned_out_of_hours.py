# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


def add_assigned_at(apps, schema_editor):
    Case = apps.get_model("legalaid", "Case")
    for case in Case.objects.all():
        case.assigned_out_of_hours = case.provider_assigned_at not in \
            settings.PROVIDER_OPENING_HOURS
        case.save()


def reverse_assigned(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0010_complaints_mi_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='assigned_out_of_hours',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
        migrations.RunPython(add_assigned_at, reverse_assigned)
    ]
