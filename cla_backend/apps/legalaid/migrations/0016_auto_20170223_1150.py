# coding=utf-8
from __future__ import unicode_literals

from django.db import migrations


def update_pd_search_field(apps, schema_editor):
    PersonalDetails = apps.get_model("legalaid", "PersonalDetails")

    for pd in PersonalDetails.objects.all().iterator():
        pd.save()


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0015_adaptationdetails_no_adaptations_required")]

    operations = [migrations.RunPython(update_pd_search_field)]
