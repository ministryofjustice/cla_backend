# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_eod_categories(apps, schema_editor):
    EODDetailsCategory = apps.get_model("legalaid", "EODDetailsCategory")
    for eod in EODDetailsCategory.objects.filter(category='scope_or_means'):
        eod.category = 'scope'
        eod.save()
        means_eod = EODDetailsCategory()
        means_eod.category = 'means'
        means_eod.eod_details = eod.eod_details
        means_eod.is_major = eod.is_major
        means_eod.save()

class Migration(migrations.Migration):

    dependencies = [
        ('legalaid', '0012_auto_20151209_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eoddetailscategory',
            name='category',
            field=models.CharField(blank=True, max_length=30, null=True, choices=[(b'incorrect', b'Believes operator has given incorrect information'), (b'scope', b'Unhappy with Operator Service determination (Scope)'), (b'means', b'Unhappy with Operator Service determination (Means)'), (b'delete', b'Wants personal details deleted'), (b'advisor_response', b'No response from specialist advisor, or response delayed'), (b'operator_delay', b'Operator service - delay in advice'), (b'operator_attitude', b"Unhappy with operator's attitude"), (b'advisor_attitude', b"Unhappy with specialist's attitude"), (b'alt_help', b'Alternative help not appropriate or not available'), (b'public_tool', b'Unhappy with online service'), (b'adaptations', b'Problems with adaptations or adjustments'), (b'scope_assessment', b'Scope reassessment requested'), (b'means_assessment', b'Financial reassessment requested'), (b'pass_to_public', b'Threatens to pass the matter on to the media, or other public or regulatory body'), (b'data_protection', b'Breach of Data Protection Act/policy and confidentiality'), (b'discrimination', b'Discrimination from an operator or specialist'), (b'plo_referral', b'Client unhappy with PLO referral'), (b'other', b'Other')]),
            preserve_default=True,
        ),
        migrations.RunPython(update_eod_categories)
    ]
