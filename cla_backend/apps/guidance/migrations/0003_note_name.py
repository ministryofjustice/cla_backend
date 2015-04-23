# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.text import slugify


note_names = {
    1: u'ASBOs and ASBIs',
    2: u'child_abuse',
    3: u'data_protection',
    4: u'debt_prompts',
    5: u'discrimination_prompts',
    6: u'discrimination_where_it_occurs',
    7: u'disregarded_benefits_list',
    8: u'domestic_abuse_signs',
    9: u'domestic_violence_definition',
    10: u'domestic_violence_prompts',
    11: u'education_admissions',
    12: u'education_discrimination_prompts',
    13: u'education_prompts',
    14: u'eligibility_check',
    15: u'exemptions',
    16: u'family_mediation',
    17: u'family_prompts',
    18: u'gender_reassignment_discrimination',
    19: u'harassment_definition',
    20: u'harassment_prompts',
    21: u'homelessness',
    22: u'homelessness_prompts',
    23: u'housing_discrimination',
    24: u'housing_disrepair',
    25: u'housing_prompts',
    26: u'injunctions',
    27: u'means_test_children',
    28: u'mortgage_reposession_timeline',
    29: u'opening_call',
    30: u'passphrase',
    31: u'protected_characteristics',
    32: u'rent_and_mortgage_payments',
    33: u'SMOD',
    34: u'special_educational_needs',
    35: u'third_party',
    36: u'unable_to_help',
    37: u'welfare_benefits',
    38: u'zero_income'
}


def set_name(apps, schema_editor):
    Note = apps.get_model('guidance', 'Note')
    for note in Note.objects.all():
        note.name = note_names.get(note.pk, slugify(note.title))
        note.save()


class Migration(migrations.Migration):

    dependencies = [
        ('guidance', '0002_remove_note_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='name',
            field=models.CharField(default='_', max_length=50),
            preserve_default=False,
        ),
        migrations.RunPython(set_name)
    ]
