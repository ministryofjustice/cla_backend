# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields
import django.utils.timezone
import uuidfield.fields
import core.cloning


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0002_auto_20150417_1122'),
    ]

    operations = [
        migrations.CreateModel(
            name='EODDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('notes', models.TextField(blank=True)),
                ('reference', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EODDetailsCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(blank=True, max_length=30, null=True, choices=[(b'incorrect', b"Believes they've been given incorrect information"), (b'cla_should_help', b'Believes CLA should be able to help with their problem'), (b'deletion', b'Wants personal details deleted'), (b'response', b"Unhappy with specialist advisor's response"), (b'delayed', b'Delay in getting correct advice'), (b'attitude', b"Unhappy with operator's attitude"), (b'alt_help', b"Alternative help not appropriate to client's issue"), (b'public_tool', b'Unhappy with public tool'), (b'accessibility', b'Accessibility problems'), (b'scope_reassess', b'Scope reassessment requested'), (b'fin_reassess', b'Financial reassessment requested'), (b'pass_to_public', b'Threatens to pass the matter on to the media, or other publilc  or regulatory body'), (b'data_protection', b'Breach of Data Protection Act'), (b'discrimination', b'Discrimination'), (b'incorrectly_reported', b'Believes CLA has incorrectly reported them under the Child, Young Person and Adult at Risk of Abuse Protection policies'), (b'other', b'Any other negative view')])),
                ('is_major', models.BooleanField(default=False)),
                ('eod_details', models.ForeignKey(related_name='categories', to='legalaid.EODDetails')),
            ],
            options={
                'abstract': False,
            },
            bases=(core.cloning.CloneModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name='case',
            name='eod_details',
            field=models.ForeignKey(blank=True, to='legalaid.EODDetails', null=True),
            preserve_default=True,
        ),
    ]
