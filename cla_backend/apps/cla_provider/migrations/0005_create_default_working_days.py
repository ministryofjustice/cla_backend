# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..models import ProviderAllocation, WorkingDays
from django.db import migrations


def create_default_working_days(_, schema_editor):
    """ Creates default WorkingDays models for all current ProviderAllocations.
    """
    db_alias = schema_editor.connection.alias

    provider_allocations = ProviderAllocation.objects.all()
    WorkingDays.objects.using(db_alias).bulk_create([WorkingDays(provider_allocation=provider_allocation) for provider_allocation in provider_allocations])


def delete_all_working_days(_, schema_editor):
    """ Removes all WorkingDays models created due to the migration.
        This is only run if the migration is reverted.
    """
    db_alias = schema_editor.connection.alias

    WorkingDays.objects.using(db_alias).all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cla_provider', '0004_create_working_days_model'),
    ]

    operations = [
        migrations.RunPython(create_default_working_days, delete_all_working_days)
    ]
