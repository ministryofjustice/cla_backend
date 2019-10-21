# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("cla_auditlog", "0001_initial"), ("complaints", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="complaint",
            name="audit_log",
            field=models.ManyToManyField(to="cla_auditlog.AuditLog"),
            preserve_default=True,
        )
    ]
