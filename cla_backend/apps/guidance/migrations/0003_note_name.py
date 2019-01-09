# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.text import slugify


note_names = {
    1: "ASBOs and ASBIs",
    2: "child_abuse",
    3: "data_protection",
    4: "debt_prompts",
    5: "discrimination_prompts",
    6: "discrimination_where_it_occurs",
    7: "disregarded_benefits_list",
    8: "domestic_abuse_signs",
    9: "domestic_violence_definition",
    10: "domestic_violence_prompts",
    11: "education_admissions",
    12: "education_discrimination_prompts",
    13: "education_prompts",
    14: "eligibility_check",
    15: "exemptions",
    16: "family_mediation",
    17: "family_prompts",
    18: "gender_reassignment_discrimination",
    19: "harassment_definition",
    20: "harassment_prompts",
    21: "homelessness",
    22: "homelessness_prompts",
    23: "housing_discrimination",
    24: "housing_disrepair",
    25: "housing_prompts",
    26: "injunctions",
    27: "means_test_children",
    28: "mortgage_reposession_timeline",
    29: "opening_call",
    30: "passphrase",
    31: "protected_characteristics",
    32: "rent_and_mortgage_payments",
    33: "SMOD",
    34: "special_educational_needs",
    35: "third_party",
    36: "unable_to_help",
    37: "welfare_benefits",
    38: "zero_income",
}


def set_name(apps, schema_editor):
    Note = apps.get_model("guidance", "Note")
    for note in Note.objects.all():
        note.name = note_names.get(note.pk, slugify(note.title))
        note.save()


class Migration(migrations.Migration):

    dependencies = [("guidance", "0002_remove_note_name")]

    operations = [
        migrations.AddField(
            model_name="note", name="name", field=models.CharField(default="_", max_length=50), preserve_default=False
        ),
        migrations.RunPython(set_name),
    ]
