# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('due', models.DateTimeField()),
                ('retried', models.IntegerField(default=0)),
                ('status', models.CharField(default=b'scheduled', max_length=20)),
                ('completed', models.BooleanField(default=False)),
                ('is_end', models.BooleanField(default=False)),
                ('notification', models.ForeignKey(to='notifications.Notification')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
