# coding=utf-8
from __future__ import unicode_literals

from django.db import migrations
from core.operations import LoadExtension


class Migration(migrations.Migration):

    dependencies = [("reports", "0001_initial")]

    operations = [LoadExtension(name="tablefunc")]
