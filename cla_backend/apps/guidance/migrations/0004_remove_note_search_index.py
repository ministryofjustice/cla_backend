# coding=utf-8
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("guidance", "0003_note_name")]

    operations = [migrations.RemoveField(model_name="note", name="search_index")]
