# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosis', '0001_initial'),
        ('legalaid', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='diagnosistraversal',
            name='category',
            field=models.ForeignKey(blank=True, to='legalaid.Category', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='diagnosistraversal',
            name='matter_type1',
            field=models.ForeignKey(related_name='+', blank=True, to='legalaid.MatterType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='diagnosistraversal',
            name='matter_type2',
            field=models.ForeignKey(related_name='+', blank=True, to='legalaid.MatterType', null=True),
            preserve_default=True,
        ),
    ]
