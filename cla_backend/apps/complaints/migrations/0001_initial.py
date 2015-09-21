# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('legalaid', '0010_complaints_mi_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('description', models.TextField(null=True, blank=True)),
                ('source', models.CharField(blank=True, max_length=15, choices=[(b'EMAIL', b'email'), (b'PHONE', b'phone'), (b'LETTER', b'letter')])),
                ('level', models.PositiveSmallIntegerField(default=11, choices=[(29, b'Major'), (11, b'Minor')])),
                ('justified', models.NullBooleanField()),
                ('resolved', models.NullBooleanField()),
                ('category', models.ForeignKey(blank=True, to='complaints.Category', null=True)),
                ('created_by', models.ForeignKey(related_name='complaints_complaint_created_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('eod', models.ForeignKey(to='legalaid.EODDetails')),
                ('owner', models.ForeignKey(related_name='complaints_complaint_owner', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=(models.Model,),
        ),
    ]
