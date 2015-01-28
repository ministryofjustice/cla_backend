# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import model_utils.fields
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DiagnosisTraversal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('reference', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('nodes', jsonfield.fields.JSONField(null=True, blank=True)),
                ('current_node_id', models.CharField(max_length=50, blank=True)),
                ('graph_version', models.CharField(max_length=50, blank=True)),
                ('state', models.CharField(default=b'UNKNOWN', max_length=50, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
