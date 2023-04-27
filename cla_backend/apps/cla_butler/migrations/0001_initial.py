# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0030_eligibilitycheck_disregards'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiversityDataCheck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('detail', models.TextField(null=True, blank=True)),
                ('action', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=10)),
                ('personal_details', models.OneToOneField(to='legalaid.PersonalDetails')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
